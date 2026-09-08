"""Constraint Engine (E01) — deterministic feasibility layer for RailMind.

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
from engine._version import (
    CONSTRAINT_SET_ID,
    CONSTRAINT_SET_VERSION,
    ENGINE_VERSION,
    PRIORITY_MODEL_ID,
    PRIORITY_MODEL_VERSION,
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
    "CONSTRAINT_SET_ID",
    "CONSTRAINT_SET_VERSION",
    "ENGINE_VERSION",
    "PRIORITY_MODEL_ID",
    "PRIORITY_MODEL_VERSION",
]
