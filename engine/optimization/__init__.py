"""Optimization Integration Layer (E03) — §17.5 objective evaluation.

Consumes E02's PriorityResult through its public contract and applies the
optimization-level coefficient β to produce an inspectable objective
breakdown for candidate maintenance plans. Deterministic; no solver, no
clocks, no randomness. E04 can consume the breakdown as its evaluation
baseline.
"""

from engine.optimization.configuration import OptimizationConfig
from engine.optimization.inputs import (
    BlockActivation,
    CandidateSolution,
    TaskAssignment,
)
from engine.optimization.evaluation import (
    ObjectiveEvaluator,
    objective_sort_key,
    rank_candidates,
)
from engine.optimization.result import ObjectiveBreakdown, PriorityComponent

__all__ = [
    "OptimizationConfig",
    "TaskAssignment",
    "BlockActivation",
    "CandidateSolution",
    "ObjectiveEvaluator",
    "objective_sort_key",
    "rank_candidates",
    "ObjectiveBreakdown",
    "PriorityComponent",
]
