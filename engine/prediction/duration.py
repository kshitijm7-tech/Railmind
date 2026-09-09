"""Duration predictor (E06) — TRD §13 / blueprint §16.1, Model 1.

**Status: deterministic baseline, not a trained model.** The authoritative
specification recommends an XGBoost Regressor "trained on synthetic historical
duration records" (§16.1); no dataset or model artifact exists in this
repository, so per TRD §50 ("ML unavailable → fallback: deterministic rules /
statistical baseline") this module ships the statistical baseline. It is
honest about that: ``algorithm="deterministic-rules"`` and the registry
metadata record ``status=DISABLED`` for the ML path.

Baseline formula (fully deterministic and inspectable):

    expected = historical_duration_minutes
             × criticality_factor(section_criticality)
             × task_type_factor(task_type)

    p10 = 0.85 × expected          # [ASSUMPTION] symmetric band factors,
    p90 = 1.25 × expected          # configurable, documented in the report

Overrun probability semantics (blueprint §16.1): "probability duration
exceeds latest_finish constraint". The threshold is resolved through
``DurationPredictionWindow`` (explicit budget > deadline-derived > default);
the baseline is a point estimate, so overrun_probability is 1.0 when the
point estimate exceeds the threshold and 0.0 otherwise — an honest step
function, never a fabricated smooth probability.
"""

from typing import Any, Dict, Optional

from engine._version import (
    DURATION_MODEL_ID,
    DURATION_MODEL_VERSION,
)
from engine.prediction.configuration import PredictionConfig
from engine.prediction.inputs import (
    DurationFeatures,
    DurationPredictionWindow,
    validate_duration_features,
)
from engine.prediction.interface import (
    ModelPredictionError,
    PredictionModel,
    require_finite,
)
from engine.prediction.registry import ModelMetadata, ModelStatus, feature_schema_version

#: [ASSUMPTION] symmetric band factors around the point estimate — the spec
#: outputs P10/expected/P90 but defines no interval width for the baseline.
P10_FACTOR = 0.85
P90_FACTOR = 1.25


def duration_model_metadata() -> ModelMetadata:
    """TRD §18 registry record for this predictor (honest baseline status)."""
    return ModelMetadata(
        model_id=DURATION_MODEL_ID,
        model_name="Maintenance Duration Prediction",
        model_type="DURATION_REGRESSION",
        version=DURATION_MODEL_VERSION,
        feature_schema_version=feature_schema_version(),
        algorithm="deterministic-rules",
        status=ModelStatus.DISABLED,  # the XGBoost artifact does not exist yet
        deterministic_fallback=True,
    )


class DurationPredictor:
    """Deterministic duration baseline implementing TRD §17's interface.

    Inference is a pure function of (features, window, config): no clock, no
    randomness, no I/O. Identical inputs produce byte-identical results.
    """

    def __init__(self, config: Optional[PredictionConfig] = None):
        self._config = config or PredictionConfig()

    @property
    def config(self) -> PredictionConfig:
        return self._config

    def get_version(self) -> str:
        """TRD §17: model version (registry identity)."""
        return DURATION_MODEL_VERSION

    def predict(
        self,
        features: DurationFeatures,
        window: Optional[DurationPredictionWindow] = None,
    ) -> "DurationPredictionResult":
        """Point prediction + interval + overrun probability (deterministic)."""
        from engine.prediction.result import DurationPredictionResult

        threshold = validate_duration_features(
            features,
            window,
            default_threshold_minutes=self._config.default_overrun_threshold_minutes,
        )

        cfg = self._config
        criticality_factor = cfg.criticality_duration_factors[features.section_criticality]
        task_type_factor = cfg.task_type_duration_factors[features.task_type]
        expected = (
            features.historical_duration_minutes * criticality_factor * task_type_factor
        )
        require_finite(expected, "predicted_duration_minutes")
        if expected <= 0.0:
            raise ModelPredictionError(
                "predicted duration must be positive; got "
                f"{expected!r} (check historical_duration_minutes input)"
            )

        p10 = expected * P10_FACTOR
        p90 = expected * P90_FACTOR
        overrun = 1.0 if expected > threshold else 0.0

        return DurationPredictionResult(
            task_id=features.task_id,
            predicted_duration_minutes=expected,
            p10_minutes=p10,
            p90_minutes=p90,
            overrun_probability=overrun,
            confidence=cfg.baseline_confidence,
            threshold_minutes=threshold,
            model_id=DURATION_MODEL_ID,
            model_version=DURATION_MODEL_VERSION,
            algorithm="deterministic-rules",
            registry_metadata=duration_model_metadata().model_dump(),
            reason_codes=self._reason_codes(features, threshold, expected),
        )

    def predict_with_uncertainty(
        self,
        features: DurationFeatures,
        window: Optional[DurationPredictionWindow] = None,
    ) -> "DurationPredictionResult":
        """TRD §17: this baseline's uncertainty evidence IS the P10/P90 band.

        Returns the same result as ``predict`` (the band is always present);
        the distinct method exists so interface consumers can rely on it for
        every model, including future ML implementations with separate
        point/uncertainty paths.
        """
        return self.predict(features, window)

    def explain(
        self,
        features: DurationFeatures,
        window: Optional[DurationPredictionWindow] = None,
    ) -> Dict[str, Any]:
        """Deterministic, data-derived explanation evidence (no prose)."""
        cfg = self._config
        return {
            "model_id": DURATION_MODEL_ID,
            "model_version": DURATION_MODEL_VERSION,
            "algorithm": "deterministic-rules",
            "feature_values": {
                "task_type": features.task_type,
                "department": features.department,
                "asset_type": features.asset_type,
                "section_criticality": features.section_criticality,
                "crew_size": features.crew_size,
                "historical_duration_minutes": features.historical_duration_minutes,
                "time_of_day_minutes": features.time_of_day_minutes,
                "days_since_last_similar_task": features.days_since_last_similar_task,
            },
            "factors_applied": {
                "criticality_factor": cfg.criticality_duration_factors[
                    features.section_criticality
                ],
                "task_type_factor": cfg.task_type_duration_factors[features.task_type],
                "p10_factor": P10_FACTOR,
                "p90_factor": P90_FACTOR,
            },
            "overrun_threshold_minutes": validate_duration_features(
                features,
                window,
                default_threshold_minutes=cfg.default_overrun_threshold_minutes,
            ),
            "baseline": True,
        }

    def _reason_codes(
        self,
        features: DurationFeatures,
        threshold: float,
        expected: float,
    ) -> list:
        codes = []
        if expected > threshold:
            codes.append("OVERRUN_RISK")
        if features.section_criticality in {"HIGH", "CRITICAL"}:
            codes.append("HIGH_CRITICALITY_SECTION")
        if features.task_type in {"EMERGENCY", "CORRECTIVE", "DEFECT"}:
            codes.append("UNPLANNED_WORK")
        if features.days_since_last_similar_task >= 180.0:
            codes.append("LONG_SINCE_SIMILAR_TASK")
        return codes


# Late import target for the result model (avoids a circular import at module
# load: result.py does not import duration.py, this import stays local).
from engine.prediction.result import DurationPredictionResult  # noqa: E402

__all__ = [
    "DurationPredictor",
    "duration_model_metadata",
    "P10_FACTOR",
    "P90_FACTOR",
]
