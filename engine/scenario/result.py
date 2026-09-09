"""Scenario comparison results (E04).

Every ranked entry retains the complete E03 ``ObjectiveBreakdown`` (never
reduced to candidate_id → float) plus the E03 solution for full auditability;
the comparison result exposes the per-term delta against the best candidate
and a neutral structured summary derived directly from the numbers.

Provenance chain E02 → E03 → E04 is preserved untouched: the ranked entry
carries the E03 breakdown (which carries per-task E02 priority model ids and
versions) and the E03 engine/optimization model identity alongside E04's own.
"""

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict

from engine._version import (
    ENGINE_VERSION,
    OPTIMIZATION_MODEL_ID,
    OPTIMIZATION_MODEL_VERSION,
    SCENARIO_MODEL_ID,
    SCENARIO_MODEL_VERSION,
)
from engine.optimization.inputs import CandidateSolution
from engine.optimization.result import ObjectiveBreakdown


class RankedCandidate(BaseModel):
    """One candidate's outcome in a completed comparison."""

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    candidate_id: str
    rank: int
    total_objective: float
    objective_delta_from_best: float  # total − best_total; best → 0.0
    objective_breakdown: ObjectiveBreakdown
    solution: CandidateSolution

    # E03 provenance, retained (never rewritten).
    optimization_model_id: str
    optimization_model_version: str
    engine_version: str

    # E04 provenance for this ranked entry.
    scenario_model_id: str
    scenario_model_version: str


class ComparisonSummary(BaseModel):
    """Structured, neutral explanation of the winner (PRD §29 / BP §21).

    Derived directly from the numeric components — no invented semantics,
    no free-text speculation. ``component_deltas`` shows how much better
    (positive) the winner is on each §17.5 term vs the runner-up; a
    negative delta means the winner is actually worse on that term and
    wins despite it.
    """

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    winner_candidate_id: str
    winner_total_objective: float
    runner_up_candidate_id: str = ""
    runner_up_total_objective: float = 0.0
    # Winner − runner-up per §17.5 term (positive = winner better on it).
    component_deltas: Dict[str, float] = {}
    total_objective_delta: float = 0.0
    deciding_components: List[str] = []
    # §17.5 terms where the winner is actually WORSE than the runner-up but
    # still wins on aggregate — kept so the audit trail never hides a loss.
    wins_despite: List[str] = []
    statement: str


class ScenarioComparison(BaseModel):
    """Deterministic outcome of comparing a set of scenario candidates."""

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    ranked: List[RankedCandidate] = []
    selected_candidate_id: str
    summary: ComparisonSummary

    scenario_model_id: str = SCENARIO_MODEL_ID
    scenario_model_version: str = SCENARIO_MODEL_VERSION
    engine_version: str = ENGINE_VERSION

    # E03/E02 lineage context (the winner's authoritative identity chain).
    optimization_model_id: str = OPTIMIZATION_MODEL_ID
    optimization_model_version: str = OPTIMIZATION_MODEL_VERSION

    def best(self) -> RankedCandidate:
        """The selected (rank-1) candidate."""
        return self.ranked[0]

    @property
    def per_candidate_priority_components(self) -> Dict[str, Any]:
        """Winner's per-task E02 priority audit trail, keyed by candidate.

        Carried through from E03's ``ObjectiveBreakdown.priority_contributions``
        (which carries E02 ``priority_model_id``/``priority_model_version`` per
        task) — never recalculated, never rewritten.
        """
        return {
            entry.candidate_id: entry.objective_breakdown.priority_contributions
            for entry in self.ranked
        }
