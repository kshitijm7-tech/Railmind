"""Planner results (E09) — the §17.3 decision-variable view + evidence.

The result exposes the solved decision variables (assignments, block
activations, timings) plus the evidence the governance layers require:

- the §17.5 objective breakdown is E03's ``ObjectiveBreakdown`` — computed
  by E03's evaluator, never re-derived inside the planner;
- solve evidence (status, wall time, seed, versions) forms the TRD §67
  reproducibility record;
- constraint trace records which §17.4 constraints bound the solution
  (blueprint §21 explainability);
- every block carries its per-window §16.3 delay evidence verbatim.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from engine._version import (
    CONSTRAINT_SET_ID,
    CONSTRAINT_SET_VERSION,
    ENGINE_VERSION,
    PLANNER_MODEL_ID,
    PLANNER_MODEL_VERSION,
)
from engine.delay.result import DelayPredictionResult
from engine.optimization.result import ObjectiveBreakdown


class TaskAssignmentResult(BaseModel):
    """§17.3 x[t,w] view: one task's assignment (or explicit unscheduled)."""

    model_config = ConfigDict(frozen=True)

    task_id: str
    # None == unscheduled[t] = 1 (explicit §17.3 slack, never a silent drop).
    window_id: Optional[str] = None


class BlockActivationResult(BaseModel):
    """§17.3 y[w] + start/end view: one activated block window."""

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    window_id: str
    section_id: str
    start: datetime  # start[w] (c7: within [e_w, l_w])
    end: datetime  # end[w] (c7: within [e_w, l_w])
    # Σ_t dur_t · x[t,w] assigned to this window (c6 workload).
    assigned_task_ids: List[str] = []
    assigned_work_minutes: float = Field(ge=0.0)
    # §16.3 delay evidence for this window, verbatim from the baseline
    # (None when the caller supplied no delay predictions for the window).
    delay_evidence: Optional[DelayPredictionResult] = None


class ConstraintTraceEntry(BaseModel):
    """One §17.4 constraint's role in bounding the solution (§21)."""

    model_config = ConfigDict(frozen=True)

    constraint_id: str
    description: str
    # How the constraint shaped the solution:
    # "binding" (active at the optimum), "active" (enforced, possibly
    # non-binding), "rejected" (made the instance infeasible for a task).
    role: str


class SolveEvidence(BaseModel):
    """TRD §67 reproducibility record for one optimization run."""

    model_config = ConfigDict(frozen=True)

    solver: str  # e.g. "cpsat" | "deterministic-sequential-fallback"
    solver_version: str
    random_seed: int
    timeout_seconds: float
    status: str  # OPTIMAL | FEASIBLE | INFEASIBLE | TIMEOUT_NO_PLAN
    wall_time_ms: float = Field(ge=0.0)
    objective_weights: Dict[str, float]
    constraint_set_id: str = CONSTRAINT_SET_ID
    constraint_set_version: str = CONSTRAINT_SET_VERSION
    engine_version: str = ENGINE_VERSION
    planner_model_id: str = PLANNER_MODEL_ID
    planner_model_version: str = PLANNER_MODEL_VERSION


class GeneratedPlan(BaseModel):
    """One solver-produced plan (the best, or one near-optimal alternative)."""

    model_config = ConfigDict(frozen=True)

    plan_id: str
    assignments: List[TaskAssignmentResult] = []
    blocks: List[BlockActivationResult] = []
    unscheduled_task_ids: List[str] = []
    # E03's evaluation of this exact solution (§17.5) — carried verbatim.
    objective: Optional[ObjectiveBreakdown] = None
    constraint_trace: List[ConstraintTraceEntry] = []


class PlannerResult(BaseModel):
    """The complete E09 planning outcome (best plan + alternatives + evidence)."""

    model_config = ConfigDict(frozen=True)

    plans: List[GeneratedPlan]  # plans[0] is the best; then alternatives
    best_plan_id: str
    evidence: SolveEvidence
    # Caller-supplied provenance echo (§15): the planner never rewrites
    # upstream identity — it stamps its own run identity alongside.
    metadata: Dict[str, Any] = {}
