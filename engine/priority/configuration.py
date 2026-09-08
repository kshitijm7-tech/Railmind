"""Priority scoring configuration (E02).

All weights and enum→score mappings live here — never hard-coded inside
factor implementations (E01 §20 discipline: business constants are
configuration).

Defaults are the authoritative PRD FR-MI-001 / blueprint §16.2 weights
(0.30 / 0.20 / 0.20 / 0.20 / 0.10) — the blueprint marks them [ASSUMPTION],
exposed as configuration so they can be tuned without code changes.
"""

from pydantic import BaseModel, ConfigDict, Field, model_validator

from engine.priority.missing_data import MissingDataPolicy


class PriorityEngineConfig(BaseModel):
    """Weights, normalization maps and classification thresholds.

    Validation:
    - every weight must be >= 0;
    - weights must not be all zero (an all-zero configuration cannot produce
      a meaningful priority and is rejected at the boundary);
    - weights are normalised to sum to 1.0 by the engine when they do not
      (explicit, deterministic, reported in metadata — never silent).
    """

    model_config = ConfigDict(frozen=True)

    # --- Factor weights (PRD FR-MI-001 defaults) -------------------------
    criticality_weight: float = Field(default=0.30, ge=0.0)
    overdue_weight: float = Field(default=0.20, ge=0.0)
    failure_risk_weight: float = Field(default=0.20, ge=0.0)
    safety_weight: float = Field(default=0.20, ge=0.0)
    downstream_impact_weight: float = Field(default=0.10, ge=0.0)

    # --- Enum→score mappings (canonical enum values → [0, 1]) ------------
    # Criticality: LOW|MEDIUM|HIGH|CRITICAL (canonical enum).
    criticality_scores: dict[str, float] = Field(
        default_factory=lambda: {
            "LOW": 0.25,
            "MEDIUM": 0.50,
            "HIGH": 0.75,
            "CRITICAL": 1.0,
        }
    )
    # Safety relevance: deterministic flags derived from the canonical task
    # contract (no hidden scoring inside factor code).
    safety_task_type_scores: dict[str, float] = Field(
        default_factory=lambda: {
            # Emergency and corrective work is safety-relevant by nature;
            # defects are unplanned degradation repairs (corrective-like);
            # preventive/inspection work is not, absent an explicit flag.
            "EMERGENCY": 1.0,
            "CORRECTIVE": 0.75,
            "DEFECT": 0.75,
            "INSPECTION": 0.25,
            "PREVENTIVE": 0.0,
        }
    )
    safety_flag_score: float = 1.0  # applied when the explicit safety flag is set
    safety_task_type_weight_share: float = Field(default=0.5, gt=0.0, le=1.0)

    # --- Overdue normalization (bounded) ----------------------------------
    # overdue_days is linearly normalised: 0 days → 0.0, saturation_days or
    # more → 1.0. Blueprint §12 demo dataset uses "3 marked overdue" tasks;
    # 30 days is the documented saturation default [ASSUMPTION, configurable].
    overdue_saturation_days: float = Field(default=30.0, gt=0.0)

    # --- Downstream impact normalization (bounded) ------------------------
    # trains_per_day is linearly normalised against this saturation value
    # (blueprint §16.2: "trains/day on this section"). 60 trains/day ≈ one
    # train per 24 minutes on a busy single line [ASSUMPTION, configurable].
    downstream_trains_per_day_saturation: float = Field(default=60.0, gt=0.0)

    # --- Classification thresholds (PRD enum: LOW|MEDIUM|HIGH|CRITICAL) ---
    # Semantics: score < medium → LOW; medium <= score < high → MEDIUM;
    # high <= score < critical → HIGH; score >= critical → CRITICAL.
    # Boundary ownership is explicit: a score exactly on a threshold belongs
    # to the higher class.
    threshold_medium: float = Field(default=0.40, ge=0.0, le=1.0)
    threshold_high: float = Field(default=0.65, ge=0.0, le=1.0)
    threshold_critical: float = Field(default=0.85, ge=0.0, le=1.0)

    # --- Missing-data policy ----------------------------------------------
    missing_data_policy: MissingDataPolicy = MissingDataPolicy.EXCLUDE_FACTOR

    # Thresholds must be strictly ordered; otherwise classification is
    # ambiguous. Fail at the configuration boundary.
    @model_validator(mode="after")
    def _validate_thresholds(self) -> "PriorityEngineConfig":
        if not (self.threshold_medium < self.threshold_high < self.threshold_critical):
            raise ValueError(
                "classification thresholds must be strictly increasing: "
                f"medium={self.threshold_medium}, high={self.threshold_high}, "
                f"critical={self.threshold_critical}"
            )
        return self

    def weights_sum(self) -> float:
        return (
            self.criticality_weight
            + self.overdue_weight
            + self.failure_risk_weight
            + self.safety_weight
            + self.downstream_impact_weight
        )

    def normalized_weights(self) -> dict[str, float]:
        """Weights renormalised to sum to 1.0 (deterministic order)."""
        total = self.weights_sum()
        if total <= 0.0:
            raise ValueError(
                "all priority weights are zero; this configuration cannot "
                "produce a meaningful priority score"
            )
        return {
            "criticality": self.criticality_weight / total,
            "overdue": self.overdue_weight / total,
            "failure_risk": self.failure_risk_weight / total,
            "safety": self.safety_weight / total,
            "downstream_impact": self.downstream_impact_weight / total,
        }
