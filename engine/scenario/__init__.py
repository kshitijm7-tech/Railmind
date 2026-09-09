"""Scenario Evaluation & Plan Comparison (E04).

Consumes E03's public contracts (CandidateSolution, ObjectiveBreakdown,
ObjectiveEvaluator) and ranks scenario candidates by the §17.5 objective.
Deterministic: neutral identifier tie-breaking, finite-objective defense,
empty/duplicate rejection. No solver, no clocks, no randomness, no I/O.
"""

from engine.scenario.inputs import ScenarioCandidate, validate_candidates
from engine.scenario.comparison import ScenarioComparator, evaluate_candidates
from engine.scenario.result import (
    ComparisonSummary,
    RankedCandidate,
    ScenarioComparison,
)

__all__ = [
    "ScenarioCandidate",
    "ScenarioComparator",
    "ComparisonSummary",
    "RankedCandidate",
    "ScenarioComparison",
    "validate_candidates",
    "evaluate_candidates",
]
