"""Objective evaluation results (E03) — inspectable §17.5 breakdown.

Every term is exposed individually plus the total, so the audit trail can
answer "how much did priority influence this result?" without re-deriving
anything. Priority factor contributions come from E02 and are carried
verbatim — never recalculated (§9).
"""

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict

from engine._version import (
    ENGINE_VERSION,
    OPTIMIZATION_MODEL_ID,
    OPTIMIZATION_MODEL_VERSION,
)


class PriorityComponent(BaseModel):
    """The β·priority contribution of one unscheduled task, with lineage."""

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    task_id: str
    priority_score: float
    beta: float
    contribution: float  # β × priority_score (positive cost in minimization)
    # E02 factor contributions, carried verbatim (never recalculated).
    factor_contributions: Dict[str, float] = {}
    # E02 provenance, retained (never overwritten).
    priority_model_id: str
    priority_model_version: str


class ObjectiveBreakdown(BaseModel):
    """Full inspectable decomposition of one §17.5 evaluation."""

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    plan_id: str
    # Each §17.5 term, exposed individually:
    train_delay_component: float            # α·Σ delay
    priority_component: float               # β·Σ unscheduled·priority
    block_count_component: float            # γ·Σ y
    overrun_risk_component: float           # δ·Σ y·overrun_risk
    bundling_component: float               # ε·Σ bundle_bonus (subtracted)
    total_objective: float                  # the §17.5 total (minimize)

    # Per-task priority detail (audit trail into E02).
    priority_contributions: List[PriorityComponent] = []

    # Weights actually used (configuration provenance).
    weights: Dict[str, float] = {}

    engine_version: str = ENGINE_VERSION
    optimization_model_id: str = OPTIMIZATION_MODEL_ID
    optimization_model_version: str = OPTIMIZATION_MODEL_VERSION

    @property
    def other_objective_components(self) -> Dict[str, float]:
        """All non-priority §17.5 terms (priority is the headline signal)."""
        return {
            "train_delay": self.train_delay_component,
            "block_count": self.block_count_component,
            "overrun_risk": self.overrun_risk_component,
            "bundling": self.bundling_component,
        }
