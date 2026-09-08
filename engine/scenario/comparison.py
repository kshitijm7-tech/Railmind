"""Deterministic scenario/plan comparison (E04).

Ranks candidates by ascending §17.5 total objective (minimization — blueprint
§17.5/§19, TRD §25) and selects the best. Deterministic end-to-end:

- pure function of (candidates, comparator configuration);
- ties resolve by the neutral, stable identifier ordering already established
  by E03 (ascending candidate_id) — never insertion order, hash order,
  randomness, or an invented semantic-importance rule (documented decision);
- finite-objective defense at the boundary (NaN/±inf rejected loudly);
- empty and duplicate candidate sets are validation errors, not silent wins.

Feasibility (E01) is intentionally out of scope here: per PRD §29 the
"Constraint status" of each plan is reported per plan by the integrating
backend; E04 compares the objective among the candidates the caller supplies.
No solver, no clocks, no randomness, no I/O.
"""

from typing import Dict, List, Optional, Sequence

from engine._version import SCENARIO_MODEL_ID, SCENARIO_MODEL_VERSION
from engine.optimization.configuration import OptimizationConfig
from engine.optimization.evaluation import ObjectiveEvaluator
from engine.optimization.inputs import CandidateSolution
from engine.scenario.inputs import ScenarioCandidate, validate_candidates
from engine.scenario.result import (
    ComparisonSummary,
    RankedCandidate,
    ScenarioComparison,
)

# §17.5 terms in canonical order (deterministic; used by delta and summary).
_OBJECTIVE_TERMS = (
    "train_delay_component",
    "priority_component",
    "block_count_component",
    "overrun_risk_component",
    "bundling_component",
)


class ScenarioComparator:
    """Compares scenario candidates by the authoritative §17.5 objective.

    E03 remains the single source of truth for objective calculation: use
    ``evaluate_candidates`` to delegate raw solutions to E03's evaluator;
    ``compare`` consumes already-evaluated ``ObjectiveBreakdown`` results.
    Neither path ever re-derives the §17.5 formula.
    """

    def compare(self, candidates: Sequence[ScenarioCandidate]) -> ScenarioComparison:
        """Rank candidates (ascending total objective; ties → ascending id).

        Pure and deterministic: identical candidates produce an identical
        ``ScenarioComparison`` regardless of input order.
        """
        candidate_list = list(candidates)
        if not candidate_list:
            raise ValueError(
                "ScenarioComparator.compare requires at least one candidate; "
                "an empty comparison is a caller error, not a silent None"
            )
        validate_candidates(candidate_list)
        _require_unique_ids(candidate_list)

        # --- Deterministic ranking (minimization: lower §17.5 = better) ---
        ordered = sorted(
            candidate_list,
            key=lambda c: (c.objective.total_objective, c.candidate_id),
        )

        best_total = ordered[0].objective.total_objective
        ranked: List[RankedCandidate] = []
        for position, candidate in enumerate(ordered, start=1):
            ranked.append(
                RankedCandidate(
                    candidate_id=candidate.candidate_id,
                    rank=position,
                    total_objective=candidate.objective.total_objective,
                    objective_delta_from_best=candidate.objective.total_objective
                    - best_total,
                    objective_breakdown=candidate.objective,
                    solution=candidate.solution,
                    optimization_model_id=candidate.objective.optimization_model_id,
                    optimization_model_version=candidate.objective.optimization_model_version,
                    engine_version=candidate.objective.engine_version,
                    scenario_model_id=SCENARIO_MODEL_ID,
                    scenario_model_version=SCENARIO_MODEL_VERSION,
                )
            )

        winner = ranked[0]
        runner_up = ranked[1] if len(ranked) > 1 else None
        summary = _build_summary(winner, runner_up)

        return ScenarioComparison(
            ranked=ranked,
            selected_candidate_id=winner.candidate_id,
            summary=summary,
        )


def evaluate_candidates(
    solutions: Sequence[CandidateSolution],
    evaluator: Optional[ObjectiveEvaluator] = None,
    config: Optional[OptimizationConfig] = None,
) -> ScenarioComparison:
    """Evaluate raw E03 solutions then compare — one convenient path.

    Delegates ALL objective computation to E03's ``ObjectiveEvaluator``
    (single source of truth; E04 never reproduces the §17.5 formula). Pass
    an evaluator/config to control the objective weights. Candidate identity
    is the solution's caller-supplied ``plan_id``.
    """
    evaluator = evaluator or ObjectiveEvaluator(config or OptimizationConfig())
    candidates = [
        ScenarioCandidate(
            candidate_id=solution.plan_id,
            solution=solution,
            objective=evaluator.evaluate(solution),
        )
        for solution in solutions
    ]
    return ScenarioComparator().compare(candidates)


def _require_unique_ids(candidates: List[ScenarioCandidate]) -> None:
    """Duplicate identities make deterministic selection ambiguous (E04 §14)."""
    seen = set()
    duplicates = []
    for candidate in candidates:
        if candidate.candidate_id in seen:
            duplicates.append(candidate.candidate_id)
        seen.add(candidate.candidate_id)
    if duplicates:
        raise ValueError(
            f"duplicate candidate_id(s): {sorted(set(duplicates))} — "
            "candidate identities must be unique for auditable, "
            "deterministic selection"
        )


def _build_summary(
    winner: RankedCandidate, runner_up: Optional[RankedCandidate]
) -> ComparisonSummary:
    """Neutral structured evidence for the winner, derived from the numbers."""
    if runner_up is None:
        return ComparisonSummary(
            winner_candidate_id=winner.candidate_id,
            winner_total_objective=winner.total_objective,
            statement=(
                f"{winner.candidate_id} selected: only candidate under "
                "evaluation (total objective "
                f"{_fmt(winner.total_objective)})."
            ),
        )

    total_delta = winner.total_objective - runner_up.total_objective
    component_deltas: Dict[str, float] = {
        term: getattr(winner.objective_breakdown, term)
        - getattr(runner_up.objective_breakdown, term)
        for term in _OBJECTIVE_TERMS
    }
    deciding = sorted(
        term for term, delta in component_deltas.items() if delta < 0.0
    )  # winner better (lower cost) on this term
    wins_despite = sorted(
        term for term, delta in component_deltas.items() if delta > 0.0
    )  # winner worse on this term but better overall

    return ComparisonSummary(
        winner_candidate_id=winner.candidate_id,
        winner_total_objective=winner.total_objective,
        runner_up_candidate_id=runner_up.candidate_id,
        runner_up_total_objective=runner_up.total_objective,
        component_deltas=component_deltas,
        total_objective_delta=total_delta,
        deciding_components=deciding,
        wins_despite=wins_despite,
        statement=(
            f"{winner.candidate_id} selected: total objective "
            f"{_fmt(winner.total_objective)} vs "
            f"{_fmt(runner_up.total_objective)} "
            f"({runner_up.candidate_id}); decided by: "
            f"{', '.join(deciding) if deciding else 'aggregate total'} "
            f"(total delta {_fmt(total_delta)})."
        ),
    )


def _fmt(value: float) -> str:
    """Stable, rounded rendering for user-facing summaries (no drift)."""
    return f"{value:.2f}"
