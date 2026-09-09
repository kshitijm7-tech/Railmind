"""E06 deterministic-baseline configuration.

Business constants are configuration, never hard-coded inside predictors
(E01 §20 discipline, inherited by every Freebuff engine). Every default is
either an authoritative specification value or a documented [ASSUMPTION]:

- ``risk classification thresholds`` — E06-owned; deliberately NOT E02's
  priority thresholds (prompt §18: do not reuse across engines unless the
  specification shares them). The spec defines no failure-risk thresholds, so
  these are explicit, documented [ASSUMPTION]s, configurable and tested.
- ``time horizon`` — TRD §15/§16.1 do not fix a numeric horizon; the 720 h
  (30-day) default is a documented [ASSUMPTION] mirroring the canonical TS
  contract default in ``engine/priority/inputs.py``.
- ``normalization saturations`` — how raw features map to [0, 1] scores;
  documented and configurable.
"""

from pydantic import BaseModel, ConfigDict, Field, model_validator

# Canonical criticality vocabulary (shared with E02 — reuse, not redefinition).
_CRITICALITY_SCORES: dict = {
    "LOW": 0.25,
    "MEDIUM": 0.50,
    "HIGH": 0.75,
    "CRITICAL": 1.0,
}

# Canonical task-type normalization for duration baselining: emergency and
# corrective work is the long-tail risk; preventive/inspection is routine.
# [ASSUMPTION] — the spec's "historical duration" feature carries the real
# signal; task type only shapes the baseline adjustment.
_TASK_TYPE_FACTORS: dict = {
    "EMERGENCY": 1.30,
    "CORRECTIVE": 1.15,
    "DEFECT": 1.15,
    "INSPECTION": 0.90,
    "PREVENTIVE": 1.00,
}


class PredictionConfig(BaseModel):
    """Configuration for the deterministic E06 baseline predictors.

    Validation: thresholds strictly increasing (classification must be
    unambiguous); saturations positive and finite; horizon positive.
    """

    model_config = ConfigDict(frozen=True)

    # --- Failure-risk classification (E06-owned thresholds) ----------------
    # Semantics: p < medium → LOW; medium ≤ p < high → MEDIUM;
    # high ≤ p < critical → HIGH; p ≥ critical → CRITICAL.
    # A probability exactly on a threshold belongs to the higher class
    # (>= semantics, matching E02's documented boundary ownership).
    risk_threshold_medium: float = Field(default=0.20, ge=0.0, le=1.0)
    risk_threshold_high: float = Field(default=0.45, ge=0.0, le=1.0)
    risk_threshold_critical: float = Field(default=0.70, ge=0.0, le=1.0)

    # --- Duration baseline --------------------------------------------------
    # Historical duration anchoring: the baseline sits between the historical
    # duration and the section-criticality / task-type adjustments.
    criticality_duration_factors: dict = Field(
        default_factory=lambda: {
            "LOW": 0.95,
            "MEDIUM": 1.00,
            "HIGH": 1.10,
            "CRITICAL": 1.20,
        }
    )
    task_type_duration_factors: dict = Field(
        default_factory=lambda: dict(_TASK_TYPE_FACTORS)
    )

    # --- Overrun semantics ---------------------------------------------------
    # Deadline-less requests use this minute budget as the overrun threshold
    # [ASSUMPTION, configurable] — an explicit window threshold always wins.
    default_overrun_threshold_minutes: float = Field(default=120.0, gt=0.0)

    # --- Failure-risk normalization saturations ------------------------------
    # Each feature is normalized to [0, 1] against a saturation point
    # [ASSUMPTION, configurable]: values at or above the saturation score 1.0.
    age_saturation_days: float = Field(default=10950.0, gt=0.0)  # 30 years
    service_gap_saturation_days: float = Field(default=365.0, gt=0.0)  # 1 year
    history_saturation_events: float = Field(default=10.0, gt=0.0)
    backlog_saturation_tasks: float = Field(default=20.0, gt=0.0)

    # --- Prediction horizon ---------------------------------------------------
    # TRD §15 does not fix a numeric horizon; 720 h (30 days) mirrors the
    # canonical TS contract default [ASSUMPTION, configurable].
    default_time_horizon_hours: float = Field(default=720.0, gt=0.0)

    # --- Confidence semantics --------------------------------------------------
    # The deterministic baseline's honesty budget: rule-based point estimates
    # are exact w.r.t. their formula, so baseline confidence is a fixed,
    # documented value — not a fabricated uncertainty estimate.
    baseline_confidence: float = Field(default=0.5, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def _validate_thresholds(self) -> "PredictionConfig":
        if not (
            self.risk_threshold_medium
            < self.risk_threshold_high
            < self.risk_threshold_critical
        ):
            raise ValueError(
                "risk classification thresholds must be strictly increasing: "
                f"medium={self.risk_threshold_medium}, "
                f"high={self.risk_threshold_high}, "
                f"critical={self.risk_threshold_critical}"
            )
        return self

    def classify_risk(self, probability: float) -> str:
        """Classify a failure probability onto the canonical enum.

        Boundary ownership: a probability exactly on a threshold belongs to
        the higher class (>= semantics).
        """
        if probability >= self.risk_threshold_critical:
            return "CRITICAL"
        if probability >= self.risk_threshold_high:
            return "HIGH"
        if probability >= self.risk_threshold_medium:
            return "MEDIUM"
        return "LOW"

    def criticality_score(self, criticality: str) -> float:
        """Canonical criticality enum → [0, 1] (E02-shared mapping)."""
        return _CRITICALITY_SCORES[criticality]

    def normalize(self, value: float, saturation: float) -> float:
        """Linear saturation normalization to [0, 1] (min(1, v/saturation))."""
        if value <= 0.0:
            return 0.0
        return min(1.0, value / saturation)


# Re-exported so adapters can validate feature models without importing the
# private module-level map (public surface stays deliberate).
CRITICALITY_SCORES = dict(_CRITICALITY_SCORES)

__all__ = ["PredictionConfig", "CRITICALITY_SCORES"]
