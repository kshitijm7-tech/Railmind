"""Asset failure-risk predictor (E06) — TRD §15, Model 4.

**Status: deterministic baseline, not a trained model.** TRD §15 recommends an
XGBoost Classifier ("Estimate likelihood that an asset becomes problematic");
no dataset or model artifact exists in this repository, so per TRD §50 ("ML
unavailable → fallback: deterministic rules / statistical baseline") this
module ships the statistical baseline. Honest labeling: the algorithm is
``deterministic-rules`` and the registry record keeps the ML path DISABLED.

Baseline formula (fully deterministic and inspectable) — a weighted mean of
normalized, documented features:

    p = w_age   · norm(asset_age_days,          age_saturation_days)
      + w_type  · type_score(asset_type)
      + w_maint · norm(maintenance_history,     history_saturation_events)
      + w_fail  · norm(failure_history,         history_saturation_events)
      + w_crit  · criticality_score(criticality)
      + w_gap   · norm(days_since_last_service, service_gap_saturation_days)
      + w_back  · norm(task_backlog,            backlog_saturation_tasks)
      + w_cond  · (1 − condition_score/100)

    p_failure = p / Σw   (true weighted mean; renormalised when features are
                          marked absent — no missing-data path exists yet
                          because every TRD §15 feature is required)

Default weights [ASSUMPTION, configurable] — degradation evidence dominates:

    age 0.15 · type 0.10 · maintenance 0.10 · failure 0.25 · criticality 0.15
    · service gap 0.10 · backlog 0.05 · condition 0.10

Risk classification uses ``PredictionConfig.classify_risk`` — E06-owned
thresholds (0.20/0.45/0.70), deliberately NOT E02's priority thresholds.
"""

from typing import Any, Dict, List, Optional

from engine._version import (
    FAILURE_RISK_MODEL_ID,
    FAILURE_RISK_MODEL_VERSION,
)
from engine.prediction.configuration import PredictionConfig
from engine.prediction.inputs import FailureRiskFeatures, validate_failure_risk_features
from engine.prediction.interface import (
    ModelPredictionError,
    PredictionModel,
    require_probability,
)
from engine.prediction.registry import ModelMetadata, ModelStatus, feature_schema_version

#: Default feature weights [ASSUMPTION] — degradation evidence dominates:
#: failure history and condition are the strongest documented predictors.
WEIGHTS: Dict[str, float] = {
    "age": 0.15,
    "asset_type": 0.10,
    "maintenance_history": 0.10,
    "failure_history": 0.25,
    "criticality": 0.15,
    "service_gap": 0.10,
    "backlog": 0.05,
    "condition": 0.10,
}

#: [ASSUMPTION] asset-type susceptibility scores — maintenance class proxies
#: (track → higher exposure, building → lower). Documented, configurable via
#: a subclassed config if a deployment needs different priors.
ASSET_TYPE_SCORES: Dict[str, float] = {
    "TRACK": 0.8,
    "SIGNAL": 0.7,
    "SWITCH": 0.9,
    "STRUCTURE": 0.5,
    "BUILDING": 0.3,
    "OTHER": 0.5,
}


def failure_risk_model_metadata() -> ModelMetadata:
    """TRD §18 registry record for this predictor (honest baseline status)."""
    return ModelMetadata(
        model_id=FAILURE_RISK_MODEL_ID,
        model_name="Asset Failure Risk Prediction",
        model_type="FAILURE_RISK_CLASSIFICATION",
        version=FAILURE_RISK_MODEL_VERSION,
        feature_schema_version=feature_schema_version(),
        algorithm="deterministic-rules",
        status=ModelStatus.DISABLED,  # the XGBoost artifact does not exist yet
        deterministic_fallback=True,
    )


def _unknown_asset_type(asset_type: str) -> ModelPredictionError:
    known = ", ".join(sorted(ASSET_TYPE_SCORES))
    return ModelPredictionError(
        f"unknown asset_type {asset_type!r}; known types: {known}. "
        "Extend ASSET_TYPE_SCORES (configuration) rather than guessing."
    )


class FailureRiskPredictor:
    """Deterministic failure-risk baseline implementing TRD §17's interface.

    Inference is a pure function of (features, config): no clock, no
    randomness, no I/O. Identical inputs produce byte-identical results.
    """

    def __init__(self, config: Optional[PredictionConfig] = None):
        self._config = config or PredictionConfig()

    @property
    def config(self) -> PredictionConfig:
        return self._config

    def get_version(self) -> str:
        """TRD §17: model version (registry identity)."""
        return FAILURE_RISK_MODEL_VERSION

    def predict(self, features: FailureRiskFeatures) -> "FailureRiskPredictionResult":
        """Failure-risk prediction (deterministic, bounded [0, 1])."""
        from engine.prediction.result import FailureRiskPredictionResult

        validate_failure_risk_features(features)
        cfg = self._config
        weights = WEIGHTS
        weight_total = sum(weights.values())

        components = {
            "age": cfg.normalize(features.asset_age_days, cfg.age_saturation_days),
            "asset_type": ASSET_TYPE_SCORES.get(features.asset_type.upper()),
            "maintenance_history": cfg.normalize(
                float(features.maintenance_history), cfg.history_saturation_events
            ),
            "failure_history": cfg.normalize(
                float(features.failure_history), cfg.history_saturation_events
            ),
            "criticality": cfg.criticality_score(features.criticality),
            "service_gap": cfg.normalize(
                features.days_since_last_service, cfg.service_gap_saturation_days
            ),
            "backlog": cfg.normalize(float(features.task_backlog), cfg.backlog_saturation_tasks),
            "condition": 1.0 - (features.condition_score / 100.0),
        }
        if components["asset_type"] is None:
            raise _unknown_asset_type(features.asset_type)

        weighted = sum(
            components[name] * weights[name] for name in weights
        )
        probability = weighted / weight_total
        require_probability(probability, "probability_of_failure")

        risk_class = cfg.classify_risk(probability)
        return FailureRiskPredictionResult(
            asset_id=features.asset_id,
            probability_of_failure=probability,
            time_horizon_hours=features.time_horizon_hours,
            risk_class=risk_class,
            confidence=cfg.baseline_confidence,
            model_id=FAILURE_RISK_MODEL_ID,
            model_version=FAILURE_RISK_MODEL_VERSION,
            algorithm="deterministic-rules",
            registry_metadata=failure_risk_model_metadata().model_dump(),
            reason_codes=self._reason_codes(features, components, risk_class),
        )

    def predict_with_uncertainty(
        self, features: FailureRiskFeatures
    ) -> "FailureRiskPredictionResult":
        """TRD §17: classification models have no interval band; the point
        prediction carries the full evidence. Distinct method for interface
        completeness (consumers can rely on it for every model)."""
        return self.predict(features)

    def explain(self, features: FailureRiskFeatures) -> Dict[str, Any]:
        """Deterministic, data-derived explanation evidence (no prose)."""
        cfg = self._config
        return {
            "model_id": FAILURE_RISK_MODEL_ID,
            "model_version": FAILURE_RISK_MODEL_VERSION,
            "algorithm": "deterministic-rules",
            "feature_values": {
                "asset_age_days": features.asset_age_days,
                "asset_type": features.asset_type,
                "maintenance_history": features.maintenance_history,
                "failure_history": features.failure_history,
                "criticality": features.criticality,
                "days_since_last_service": features.days_since_last_service,
                "task_backlog": features.task_backlog,
                "condition_score": features.condition_score,
            },
            "normalized_components": {
                "age": cfg.normalize(features.asset_age_days, cfg.age_saturation_days),
                "asset_type": ASSET_TYPE_SCORES.get(features.asset_type.upper()),
                "maintenance_history": cfg.normalize(
                    float(features.maintenance_history), cfg.history_saturation_events
                ),
                "failure_history": cfg.normalize(
                    float(features.failure_history), cfg.history_saturation_events
                ),
                "criticality": cfg.criticality_score(features.criticality),
                "service_gap": cfg.normalize(
                    features.days_since_last_service, cfg.service_gap_saturation_days
                ),
                "backlog": cfg.normalize(
                    float(features.task_backlog), cfg.backlog_saturation_tasks
                ),
                "condition": 1.0 - (features.condition_score / 100.0),
            },
            "weights": dict(WEIGHTS),
            "risk_thresholds": {
                "medium": cfg.risk_threshold_medium,
                "high": cfg.risk_threshold_high,
                "critical": cfg.risk_threshold_critical,
            },
            "time_horizon_hours": features.time_horizon_hours,
            "baseline": True,
        }

    def _reason_codes(
        self,
        features: FailureRiskFeatures,
        components: Dict[str, Optional[float]],
        risk_class: str,
    ) -> List[str]:
        codes: List[str] = []
        if components["failure_history"] >= 1.0:
            codes.append("SATURATED_FAILURE_HISTORY")
        elif components["failure_history"] > 0.0:
            codes.append("FAILURE_HISTORY_PRESENT")
        if components["condition"] >= 0.5:
            codes.append("LOW_CONDITION_SCORE")
        if components["service_gap"] >= 1.0:
            codes.append("SERVICE_GAP_AT_SATURATION")
        if components["criticality"] >= 0.75:
            codes.append("HIGH_CRITICALITY_ASSET")
        if risk_class == "CRITICAL":
            codes.append("RISK_CLASS_CRITICAL")
        return codes


# Late import target for the result model (avoids a circular import at module
# load: result.py does not import this module).
from engine.prediction.result import FailureRiskPredictionResult  # noqa: E402

__all__ = [
    "FailureRiskPredictor",
    "failure_risk_model_metadata",
    "WEIGHTS",
    "ASSET_TYPE_SCORES",
]
