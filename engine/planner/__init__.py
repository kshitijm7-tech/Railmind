"""§17 CP-SAT optimization engine (E09) — the Tier-1 scheduling engine.

Blueprint §17.1–§17.4 + TRD §22–§25: CP-SAT model over candidate block
windows, enforcing all nine hard constraints (c1–c9), producing the best
plan plus near-optimal alternatives, each evaluated by E03's exact §17.5
objective evaluator. Deterministic given (input, config): num_workers=1,
explicit random_seed (blueprint §26, TRD §67).

Identity: ``railmind-cpsat-planner`` (engine._version).

Dependency discipline (§21/§22): ortools is imported ONLY inside this
package (cpsat_model.py / solver.py); the delay baseline
(engine/delay) stays ortools-free so the deterministic engines remain
importable in minimal environments.
"""

from engine.planner.configuration import PlannerConfig
from engine.planner.cpsat_model import (
    C1_ASSIGNMENT,
    C2_ACTIVATION,
    C3_QUALIFICATION,
    C4_CREW_CAPACITY,
    C5_SECTION_EXCLUSIVITY,
    C6_DURATION_FEASIBILITY,
    C7_WINDOW_BOUNDS,
    C8_PRECEDENCE,
    C9_DEADLINE,
    PlannerModel,
)
from engine.planner.errors import PlannerError
from engine.planner.inputs import (
    CrewPool,
    PlannerInput,
    TaskInput,
    WindowInput,
)
from engine.planner.result import (
    BlockActivationResult,
    ConstraintTraceEntry,
    GeneratedPlan,
    PlannerResult,
    SolveEvidence,
    TaskAssignmentResult,
)
from engine.planner.solver import CpSatPlanner

__all__ = [
    "PlannerConfig",
    "PlannerModel",
    "C1_ASSIGNMENT",
    "C2_ACTIVATION",
    "C3_QUALIFICATION",
    "C4_CREW_CAPACITY",
    "C5_SECTION_EXCLUSIVITY",
    "C6_DURATION_FEASIBILITY",
    "C7_WINDOW_BOUNDS",
    "C8_PRECEDENCE",
    "C9_DEADLINE",
    "PlannerError",
    "CrewPool",
    "PlannerInput",
    "TaskInput",
    "WindowInput",
    "BlockActivationResult",
    "ConstraintTraceEntry",
    "GeneratedPlan",
    "PlannerResult",
    "SolveEvidence",
    "TaskAssignmentResult",
    "CpSatPlanner",
]
