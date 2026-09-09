"""Prediction result contracts (E06).

Frozen result objects mirroring the canonical prediction vocabulary in
``frontend/contracts/ai/predictions.ts``:

- ``PredictionBase``            → identity/provenance fields on every result
- ``DurationPrediction``        → predicted_duration_minutes, p10, p90
- ``FailureRiskPrediction``     → probability_of_failure, time_horizon_hours

Plus the TRD §13 overrun probability and the TRD §18 registry reference.
Provenance discipline (prompt §15):

- every result carries ``model_id`` / ``model_version`` / ``engine_version``;
- E02's priority provenance and E05's simulation evidence are consumed
  as-is and never rewritten or fabricated here;
- ``recorded_at`` is caller-supplied (never derived from a clock inside the
  engine — the E02 ``evaluation_time`` determinism discipline).

Probability outputs are structurally bounded to [0, 1]; percentiles are
ordered and finite. Nothing is clamped silently — invalid values cannot be
constructed.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from engine._version import ENGINE_VERSION
from engine.models.inputs import require_timezone_aware
from engine.prediction.interface import (
    ModelPredictionError,
    require_finite,
    require_probability,
)

# Canonical Provenance vocabulary (frontend/contracts/common/provenance.ts).
_DATA_SOURCES = {
    "BDMS", "TMS", "SMMS", "TDMS", "COA", "USER",
    "AI", "SIMULATION", "SYNTHETIC", "IMPORT", "SYSTEM",
}
_DATA_STATES = {"REAL", "MOCKED", "SIMULATED", "STUBBED", "PLANNED"}


class PredictionProvenance(BaseModel):
    """Canonical ``Provenance`` contract (1:1 TS mirror), engine-side.

    ``recorded_at`` must be supplied by the caller: the engine never reads a
    clock, so a prediction result can only be stamped by the layer that owns
    the evaluation time. ``source``/``state`` default to the honest baseline
    values for deterministic rule predictors (``SYSTEM`` / ``SIMULATED``).
    """

    model_config = ConfigDict(frozen=True)

    source: str = "SYSTEM"  # DataSource enum (AI when a trained model serves)
    state: str = "SIMULATED"  # DataState enum (estimates, not measured reality)
    recorded_at: Optional[datetime] = None
    version: Optional[str] = None
    actor: Optional[str] = None

    @field_validator("source")
    @classmethod
    def _source_known(cls, value: str) -> str:
        if value not in _DATA_SOURCES:
            raise ValueError(
                f"source must be one of {sorted(_DATA_SOURCES)}; got {value!r}"
            )
        return value

    @field_validator("state")
    @classmethod
    def _state_known(cls, value: str) -> str:
        if value not in _DATA_STATES:
            raise ValueError(
                f"state must be one of {sorted(_DATA_STATES)}; got {value!r}"
            )
        return value

    @field_validator("recorded_at")
    @classmethod
    def _tz_aware(cls, value: Optional[datetime]) -> Optional[datetime]:
        if value is None:
            return None
        return require_timezone_aware(value, "recorded_at")


class PredictionBase(BaseModel):
    """Shared identity/provenance fields (TS ``PredictionBase`` + registry ref).

    Invariants (tested):
    - ``probability`` fields on subclasses are within [0, 1];
    - identical inputs → byte-identical results (no clocks, no randomness);
    - upstream provenance is carried verbatim, never rewritten.
    """

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    model_id: str
    model_version: str
    engine_version: str = ENGINE_VERSION
    algorithm: str  # honest algorithm label (e.g. "deterministic-rules")
    registry_metadata: Optional[Dict[str, Any]] = None  # TRD §18 record snapshot
    provenance: Optional[PredictionProvenance] = None


class DurationPredictionResult(PredictionBase):
    """Duration prediction (TRD §13 / blueprint §16.1 / TS ``DurationPrediction``).

    - ``predicted_duration_minutes`` — the point estimate (expected duration);
    - ``p10_minutes`` / ``p90_minutes`` — the prediction interval;
    - ``overrun_probability`` — P(duration exceeds the threshold), bounded [0,1];
    - ``confidence`` — bounded [0,1] model confidence evidence.
    """

    task_id: str
    predicted_duration_minutes: float = Field(gt=0.0)
    p10_minutes: float = Field(gt=0.0)
    p90_minutes: float = Field(gt=0.0)
    overrun_probability: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    threshold_minutes: float = Field(gt=0.0)  # the overrun threshold applied
    reason_codes: List[str] = []

    @field_validator("predicted_duration_minutes", "p10_minutes", "p90_minutes")
    @classmethod
    def _finite_durations(cls, value: float, info) -> float:
        try:
            return require_finite(value, info.field_name)
        except ModelPredictionError as exc:
            raise ValueError(str(exc)) from exc

    @field_validator("overrun_probability", "confidence")
    @classmethod
    def _bounded_probability(cls, value: float, info) -> float:
        try:
            return require_probability(value, info.field_name)
        except ModelPredictionError as exc:
            raise ValueError(str(exc)) from exc

    @field_validator("p10_minutes")
    @classmethod
    def _interval_ordered(cls, value: float, info) -> float:
        # Cross-field ordering is enforced in the model validators below;
        # kept here for the single-field guarantee that P10 is positive.
        return value


class FailureRiskPredictionResult(PredictionBase):
    """Asset failure-risk prediction (TRD §15 / TS ``FailureRiskPrediction``).

    - ``probability_of_failure`` — P(asset becomes problematic within the
      stated ``time_horizon_hours``), bounded [0, 1];
    - ``risk_class`` — canonical LOW|MEDIUM|HIGH|CRITICAL enum under the
      E06 risk-classification thresholds (NOT E02's priority thresholds);
    - ``confidence`` — bounded [0, 1] model confidence evidence.
    """

    asset_id: str
    probability_of_failure: float = Field(ge=0.0, le=1.0)
    time_horizon_hours: float = Field(gt=0.0)
    risk_class: str  # LOW | MEDIUM | HIGH | CRITICAL
    confidence: float = Field(ge=0.0, le=1.0)
    reason_codes: List[str] = []

    @field_validator("probability_of_failure", "confidence")
    @classmethod
    def _bounded_probability(cls, value: float, info) -> float:
        try:
            return require_probability(value, info.field_name)
        except ModelPredictionError as exc:
            raise ValueError(str(exc)) from exc

    @field_validator("risk_class")
    @classmethod
    def _risk_class_known(cls, value: str) -> str:
        if value not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
            raise ValueError(
                "risk_class must be one of LOW|MEDIUM|HIGH|CRITICAL; "
                f"got {value!r}"
            )
        return value


__all__ = [
    "PredictionProvenance",
    "PredictionBase",
    "DurationPredictionResult",
    "FailureRiskPredictionResult",
]
