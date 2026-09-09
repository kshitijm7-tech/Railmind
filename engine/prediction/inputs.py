"""Feature and window input contracts (E06).

Mirrors the exact documented feature lists — no invented features, no
renames, no speculative extras:

- TRD §13 / blueprint §16.1 (duration prediction): task_type, department,
  asset_type, section criticality, crew size, historical duration for this
  task/asset type, time-of-day, day count since last similar task.
- TRD §15 (asset failure/risk): asset_age, asset_type, maintenance_history,
  failure_history, criticality, days_since_last_service, task_backlog,
  condition_score.

Validation follows E02–E05 discipline: canonical enums only, finite numbers,
loud rejection (NaN/±Infinity/out-of-range never clamp), timezone-aware
datetimes, frozen models. Model inputs are plain engine data — never ML
library objects (prompt §5).
"""

import math
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from engine.models.inputs import require_timezone_aware
from engine.prediction.interface import require_finite
from engine.priority.inputs import TASK_TYPES

#: Canonical criticality vocabulary (shared with E02 — reuse, not redefinition).
SectionCriticality = str  # LOW | MEDIUM | HIGH | CRITICAL

_CRITICALITY = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


def _require_criticality(value: str, field_name: str) -> str:
    if value not in _CRITICALITY:
        raise ValueError(
            f"{field_name} must be one of LOW|MEDIUM|HIGH|CRITICAL; got {value!r}"
        )
    return value


def _require_finite_field(value: float, field_name: str) -> float:
    try:
        return require_finite(value, field_name)
    except Exception as exc:  # ModelPredictionError is a ValueError subclass
        raise ValueError(str(exc)) from exc


class DurationFeatures(BaseModel):
    """TRD §13 / blueprint §16.1 duration-prediction feature vector.

    Every documented feature is required — the deterministic baseline
    normalizes with all of them, and a trained model would pin this exact
    schema (``feature_schema_version``). Missing data must be supplied by the
    caller or the prediction is refused; the engine never invents features.
    """

    model_config = ConfigDict(frozen=True)

    task_id: str

    # --- TRD §13 feature list (exact order for schema documentation) ------
    task_type: str  # canonical task vocabulary (PREVENTIVE|CORRECTIVE|INSPECTION|EMERGENCY|DEFECT)
    department: str
    asset_type: str
    section_criticality: SectionCriticality  # LOW|MEDIUM|HIGH|CRITICAL
    crew_size: int = Field(ge=0)
    historical_duration_minutes: float = Field(ge=0.0)
    time_of_day_minutes: float = Field(ge=0.0, lt=1440.0)  # minutes since midnight
    days_since_last_similar_task: float = Field(ge=0.0)

    @field_validator("task_type")
    @classmethod
    def _task_type_known(cls, value: str) -> str:
        normalized = value.upper()
        if normalized not in TASK_TYPES:
            raise ValueError(
                "task_type must be one of PREVENTIVE|CORRECTIVE|INSPECTION|"
                f"EMERGENCY|DEFECT (either canonical vocabulary); got {value!r}"
            )
        return normalized

    @field_validator("section_criticality")
    @classmethod
    def _criticality_known(cls, value: str) -> str:
        return _require_criticality(value, "section_criticality")

    @field_validator(
        "historical_duration_minutes",
        "time_of_day_minutes",
        "days_since_last_similar_task",
    )
    @classmethod
    def _finite(cls, value: float, info) -> float:
        return _require_finite_field(value, info.field_name)


class DurationPredictionWindow(BaseModel):
    """The scheduling context an overrun probability is evaluated against.

    Overrun semantics (TRD §13 / blueprint §16.1): the probability that the
    task duration exceeds the ``latest_finish`` constraint. ``latest_finish``
    is the blueprint §11.2 field already carried by E01's ``TaskRequirement``.
    Deadline-based evaluation requires ``start_at`` (the deterministic start
    reference) so the deadline converts to a minute budget; an explicit
    ``overrun_threshold_minutes`` overrides the deadline entirely.
    """

    model_config = ConfigDict(frozen=True)

    start_at: Optional[datetime] = None
    latest_finish: Optional[datetime] = None
    overrun_threshold_minutes: Optional[float] = Field(default=None, gt=0.0)

    @field_validator("start_at", "latest_finish")
    @classmethod
    def _tz_aware(cls, value: Optional[datetime]) -> Optional[datetime]:
        if value is None:
            return None
        return require_timezone_aware(value, "window instant")

    @field_validator("overrun_threshold_minutes")
    @classmethod
    def _finite_threshold(cls, value: Optional[float]) -> Optional[float]:
        if value is None:
            return None
        return _require_finite_field(value, "overrun_threshold_minutes")

    def resolved_threshold_minutes(self, default_minutes: float) -> float:
        """Threshold resolution order: explicit > deadline-derived > default.

        Raises when a deadline is supplied without ``start_at`` (a minute
        budget cannot be derived and none is invented).
        """
        if self.overrun_threshold_minutes is not None:
            return self.overrun_threshold_minutes
        if self.latest_finish is not None:
            if self.start_at is None:
                raise ValueError(
                    "latest_finish was supplied without start_at; the overrun "
                    "threshold cannot be derived and is never guessed"
                )
            if self.latest_finish <= self.start_at:
                raise ValueError(
                    "latest_finish must be after start_at; got an empty or "
                    "negative budget"
                )
            return (self.latest_finish - self.start_at).total_seconds() / 60.0
        return default_minutes


class FailureRiskFeatures(BaseModel):
    """TRD §15 asset failure/risk feature vector (exact documented list)."""

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    asset_id: str

    # --- TRD §15 feature list ---------------------------------------------
    asset_age_days: float = Field(ge=0.0)
    asset_type: str
    maintenance_history: int = Field(ge=0)  # past maintenance events
    failure_history: int = Field(ge=0)  # past failure events
    criticality: SectionCriticality  # LOW|MEDIUM|HIGH|CRITICAL
    days_since_last_service: float = Field(ge=0.0)
    task_backlog: int = Field(ge=0)
    condition_score: float = Field(ge=0.0, le=100.0)  # 0 (failed) .. 100 (as new)

    # Prediction horizon (mirrors frontend ``FailureRiskPrediction``):
    # P(failure within horizon) — default 720 h = 30 days.
    time_horizon_hours: float = Field(default=720.0, gt=0.0)

    @field_validator("criticality")
    @classmethod
    def _criticality_known(cls, value: str) -> str:
        return _require_criticality(value, "criticality")

    @field_validator("asset_age_days", "days_since_last_service")
    @classmethod
    def _finite(cls, value: float, info) -> float:
        return _require_finite_field(value, info.field_name)


def validate_duration_features(
    features: DurationFeatures,
    window: Optional[DurationPredictionWindow] = None,
    default_threshold_minutes: float = 120.0,
) -> float:
    """Cross-field validation for a duration prediction request.

    Returns the resolved overrun threshold in minutes. Resolution order:
    explicit ``overrun_threshold_minutes`` > deadline-derived budget
    (``latest_finish`` − ``start_at``) > configured default. Raises when a
    deadline is supplied without a start reference — no threshold is ever
    invented.
    """
    return _resolve_threshold(window, default_threshold_minutes)


def _resolve_threshold(
    window: Optional[DurationPredictionWindow], default_minutes: float
) -> float:
    if window is None:
        return default_minutes
    return window.resolved_threshold_minutes(default_minutes)


def validate_failure_risk_features(features: FailureRiskFeatures) -> None:
    """Cross-field validation hook for failure-risk requests.

    All TRD §15 features are individually validated at the model boundary;
    no additional cross-field rule is specified. Kept as the explicit public
    validation entry point so callers get one uniform validation API across
    both predictors (and future adapters have a single hook).
    """
    return None


__all__ = [
    "DurationFeatures",
    "DurationPredictionWindow",
    "FailureRiskFeatures",
    "validate_duration_features",
    "validate_failure_risk_features",
]
