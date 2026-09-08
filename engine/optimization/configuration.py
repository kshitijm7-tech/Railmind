"""Optimization configuration (E03) — the §17.5 objective weights.

Defaults are the authoritative blueprint §17.5 / TRD §25 values, marked
[ASSUMPTION] in the blueprint and explicitly designed as configuration
("expose as sliders in the planning UI so judges can see the trade-off live"):

    Minimize  α·Σ_r delay_r
            + β·Σ_t unscheduled_t · priority_t
            + γ·Σ_w y_w
            + δ·Σ_w y_w · overrun_risk(w)
            - ε·Σ bundle_bonus
    defaults: α=5, β=4, γ=1, δ=2, ε=1

β is the OPTIMIZATION-level priority coefficient. It is deliberately distinct
from E02's internal factor weights (0.30/0.20/0.20/0.20/0.10), which shape the
priority score itself; β only controls how strongly the already-computed
priority score participates in this objective.
"""

from pydantic import BaseModel, ConfigDict, Field


class OptimizationConfig(BaseModel):
    """Objective weights and evaluation settings (all validated, none hidden)."""

    model_config = ConfigDict(frozen=True)

    # --- §17.5 objective weights (blueprint/TRD defaults) -----------------
    train_delay_weight: float = Field(default=5.0, ge=0.0)          # α
    unscheduled_priority_weight: float = Field(default=4.0, ge=0.0)  # β
    block_count_weight: float = Field(default=1.0, ge=0.0)          # γ
    overrun_risk_weight: float = Field(default=2.0, ge=0.0)         # δ
    bundling_weight: float = Field(default=1.0, ge=0.0)             # ε

    # --- Deterministic ranking tie-break (documented decision) ------------
    # The specification defines no tie-breaking rule; E03 therefore uses a
    # neutral, stable identifier ordering (plan_id, then task ids) — never an
    # invented semantic-importance rule. See docs/E03_Report.md §16.
    # (No configuration value required; ordering is defined in evaluation.py.)

    def objective_weights(self) -> dict:
        """Weights as a named mapping (deterministic order, for traces)."""
        return {
            "train_delay": self.train_delay_weight,
            "unscheduled_priority": self.unscheduled_priority_weight,
            "block_count": self.block_count_weight,
            "overrun_risk": self.overrun_risk_weight,
            "bundling": self.bundling_weight,
        }
