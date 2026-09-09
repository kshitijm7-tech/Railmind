"""Constraints package: rules, engine, result model, configuration.

Public API re-exported at the package level for consumers.
"""

from engine.constraints.base import ConstraintRule
from engine.constraints.engine import ConstraintEngine, default_rules
from engine.constraints.result import (
    ConstraintEvaluation,
    ConstraintEvidence,
    ConstraintResult,
    EngineError,
)
from engine.constraints.types import ConstraintType
from engine.constraints.severity import ConstraintSeverity
from engine.constraints.configuration import ConstraintEngineConfig

__all__ = [
    "ConstraintRule",
    "ConstraintEngine",
    "default_rules",
    "ConstraintEvaluation",
    "ConstraintEvidence",
    "ConstraintResult",
    "EngineError",
    "ConstraintType",
    "ConstraintSeverity",
    "ConstraintEngineConfig",
]
