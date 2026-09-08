"""Priority Engine (E02) — deterministic, explainable maintenance priority.

Pure Python; no FastAPI, SQLAlchemy, network, persistence, clocks or
randomness. Consumed by E03 as an objective input.
"""

from engine.priority.configuration import PriorityEngineConfig
from engine.priority.engine import PriorityEngine, classify
from engine.priority.inputs import (
    AssetContext,
    AssetFailureRisk,
    PriorityInput,
    SectionContext,
    TaskType,
)
from engine.priority.missing_data import MissingDataPolicy
from engine.priority.result import FactorScore, PriorityResult

__all__ = [
    "PriorityEngine",
    "PriorityEngineConfig",
    "classify",
    "PriorityInput",
    "AssetContext",
    "AssetFailureRisk",
    "SectionContext",
    "TaskType",
    "MissingDataPolicy",
    "PriorityResult",
    "FactorScore",
]
