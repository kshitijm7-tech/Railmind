"""§17.5 objective evaluation (E03).

Deterministic evaluation of a candidate solution against the blueprint's
maintenance-optimization objective. This module implements the E03 boundary:
it CONSUMES E02's ``PriorityResult`` (score + factor contributions +
provenance) and applies the optimization-level coefficient β. It never
recomputes, re-derives or substitutes priority values.

    Minimize  α·Σ_r delay_r
            + β·Σ_t unscheduled_t · priority_t
            + γ·Σ_w y_w
            + δ·Σ_w y_w · overrun_risk(w)
            - ε·Σ bundle_bonus

Sign convention (§17.5 is a MINIMIZATION objective, blueprint §17.5 / TRD
§25): priority appears as a positive COST for leaving high-priority
maintenance unscheduled. Scheduled tasks contribute zero to the β term —
rewarding their scheduling is implicit (they avoid the cost). The bundling
reward is subtracted (−ε), exactly as specified.

Feasibility separation (§11): this layer evaluates objective quality only.
Hard constraints belong to E01; a candidate that violates a hard constraint
must be rejected by the caller before objective comparison. Nothing in E03
can relax an E01 result.
"""

from typing import Dict, List

import math

from engine.optimization.configuration import OptimizationConfig
from engine.optimization.inputs import CandidateSolution, TaskAssignment
from engine.optimization.result import ObjectiveBreakdown, PriorityComponent
from engine.priority.result import PriorityResult


class ObjectiveEvaluator:
    """Evaluates candidate solutions against the §17.5 objective.

    Deterministic: pure function of (solution, configuration). No clocks,
    randomness, I/O or hidden state.
    """

    def __init__(self, config: OptimizationConfig = None):
        self._config = config or OptimizationConfig()

    @property
    def config(self) -> OptimizationConfig:
        return self._config

    def evaluate(self, solution: CandidateSolution) -> ObjectiveBreakdown:
        cfg = self._config

        # --- α·Σ_r delay_r ------------------------------------------------
        delay_component = cfg.train_delay_weight * solution.total_train_delay_minutes

        # --- β·Σ_t unscheduled_t · priority_t -----------------------------
        priority_components: List[PriorityComponent] = []
        priority_total = 0.0
        for assignment in solution.unscheduled_tasks:
            priority = assignment.priority
            assert priority is not None  # enforced by TaskAssignment validation
            _validate_priority_score(assignment.task_id, priority)
            contribution = cfg.unscheduled_priority_weight * priority.score
            priority_total += contribution
            priority_components.append(
                PriorityComponent(
                    task_id=assignment.task_id,
                    priority_score=priority.score,
                    beta=cfg.unscheduled_priority_weight,
                    contribution=contribution,
                    factor_contributions={
                        f.factor: f.contribution for f in priority.factor_scores
                    },
                    priority_model_id=priority.priority_model_id,
                    priority_model_version=priority.priority_model_version,
                )
            )

        # --- γ·Σ_w y_w -----------------------------------------------------
        block_count_component = cfg.block_count_weight * len(solution.blocks)

        # --- δ·Σ_w y_w · overrun_risk(w) -----------------------------------
        overrun_component = cfg.overrun_risk_weight * sum(
            b.overrun_risk for b in solution.blocks
        )

        # --- ε·Σ bundle_bonus (reward → subtracted in minimization) --------
        bundling_component = cfg.bundling_weight * sum(
            b.bundle_bonus for b in solution.blocks
        )

        total = (
            delay_component
            + priority_total
            + block_count_component
            + overrun_component
            - bundling_component
        )

        return ObjectiveBreakdown(
            plan_id=solution.plan_id,
            train_delay_component=delay_component,
            priority_component=priority_total,
            block_count_component=block_count_component,
            overrun_risk_component=overrun_component,
            bundling_component=bundling_component,
            total_objective=total,
            priority_contributions=priority_components,
            weights=cfg.objective_weights(),
        )


def _validate_priority_score(task_id: str, priority: PriorityResult) -> None:
    """E03 boundary defense (§17 numerical safety).

    E02's contract guarantees ``score`` ∈ [0, 1]. Anything non-finite or
    outside that range is a contract violation: fail loudly, never clamp or
    propagate NaN into the objective.
    """
    score = priority.score
    if not math.isfinite(score) or score < 0.0 or score > 1.0:
        raise ValueError(
            f"E02 contract violation for task {task_id!r}: priority score "
            f"must be finite and within [0, 1]; got {score!r}"
        )


def objective_sort_key(breakdown: ObjectiveBreakdown):
    """Neutral, stable ranking key (smaller objective = better).

    Tie-breaking (§16): the specification defines no tie-break rule, so a
    neutral identifier ordering (plan_id) is used — never an invented
    semantic-importance rule.
    """
    return (breakdown.total_objective, breakdown.plan_id)


def rank_candidates(breakdowns: List[ObjectiveBreakdown]) -> List[ObjectiveBreakdown]:
    """Rank candidate evaluations: lower §17.5 total is better; ties broken
    by neutral plan_id ordering (documented decision, §16)."""
    return sorted(breakdowns, key=objective_sort_key)
