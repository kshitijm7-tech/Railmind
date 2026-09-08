"""Freebuff intelligence engines for RailMind.

E01 — Constraint Engine (engine.constraints)
E02 — Priority Engine (engine.priority)
E03 — Optimization Integration Layer (engine.optimization)
E04 — Scenario Evaluation & Plan Comparison (engine.scenario)

Pure Python. No FastAPI, no SQLAlchemy, no network, no persistence, no clock.
"""

from engine.constraints.engine import ConstraintEngine, ConstraintEvaluation, default_rules
from engine.constraints.result import ConstraintResult, ConstraintEvidence, EngineError
from engine.constraints.types import ConstraintType
from engine.constraints.severity import ConstraintSeverity
from engine.constraints.configuration import ConstraintEngineConfig
from engine.priority.engine import PriorityEngine, classify
from engine.priority.configuration import PriorityEngineConfig
from engine.priority.inputs import PriorityInput, AssetFailureRisk, TaskType
from engine.priority.missing_data import MissingDataPolicy
from engine.priority.result import PriorityResult, FactorScore
from engine.optimization import (
    BlockActivation,
    CandidateSolution,
    ObjectiveBreakdown,
    ObjectiveEvaluator,
    OptimizationConfig,
    PriorityComponent,
    TaskAssignment,
    rank_candidates,
)
from engine.scenario import (
    ComparisonSummary,
    RankedCandidate,
    ScenarioCandidate,
    ScenarioComparator,
    ScenarioComparison,
    evaluate_candidates,
    validate_candidates,
)
from engine._version import (
    CONSTRAINT_SET_ID,
    CONSTRAINT_SET_VERSION,
    ENGINE_VERSION,
    OPTIMIZATION_MODEL_ID,
    OPTIMIZATION_MODEL_VERSION,
    PRIORITY_MODEL_ID,
    PRIORITY_MODEL_VERSION,
    SCENARIO_MODEL_ID,
    SCENARIO_MODEL_VERSION,
)

__all__ = [
    "ConstraintEngine",
    "default_rules",
    "ConstraintEvaluation",
    "ConstraintResult",
    "ConstraintEvidence",
    "EngineError",
    "ConstraintType",
    "ConstraintSeverity",
    "ConstraintEngineConfig",
    "PriorityEngine",
    "classify",
    "PriorityEngineConfig",
    "PriorityInput",
    "AssetFailureRisk",
    "TaskType",
    "MissingDataPolicy",
    "PriorityResult",
    "FactorScore",
    "OptimizationConfig",
    "TaskAssignment",
    "BlockActivation",
    "CandidateSolution",
    "ObjectiveEvaluator",
    "ObjectiveBreakdown",
    "PriorityComponent",
    "rank_candidates",
    "ScenarioCandidate",
    "ScenarioComparator",
    "ScenarioComparison",
    "RankedCandidate",
    "ComparisonSummary",
    "evaluate_candidates",
    "validate_candidates",
    "CONSTRAINT_SET_ID",
    "CONSTRAINT_SET_VERSION",
    "ENGINE_VERSION",
    "PRIORITY_MODEL_ID",
    "PRIORITY_MODEL_VERSION",
    "OPTIMIZATION_MODEL_ID",
    "OPTIMIZATION_MODEL_VERSION",
    "SCENARIO_MODEL_ID",
    "SCENARIO_MODEL_VERSION",
]
