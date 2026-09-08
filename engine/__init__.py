"""Constraint Engine (E01) — deterministic feasibility layer for RailMind.

Pure Python. No FastAPI, no SQLAlchemy, no network, no persistence, no clock.
"""

from engine.constraints.engine import ConstraintEngine, ConstraintEvaluation, default_rules
from engine.constraints.result import ConstraintResult, ConstraintEvidence, EngineError
from engine.constraints.types import ConstraintType
from engine.constraints.severity import ConstraintSeverity
from engine.constraints.configuration import ConstraintEngineConfig
from engine._version import CONSTRAINT_SET_ID, CONSTRAINT_SET_VERSION, ENGINE_VERSION

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
    "CONSTRAINT_SET_ID",
    "CONSTRAINT_SET_VERSION",
    "ENGINE_VERSION",
]
