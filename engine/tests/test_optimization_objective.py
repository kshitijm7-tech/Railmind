"""Tests — E03 objective evaluation: exact §17.5 math, β semantics, boundaries."""

import pytest

from engine.optimization.configuration import OptimizationConfig
from engine.optimization.evaluation import ObjectiveEvaluator, rank_candidates
from engine.optimization.inputs import BlockActivation, CandidateSolution, TaskAssignment
from engine.priority.configuration import PriorityEngineConfig
from engine.priority.engine import PriorityEngine
from engine.priority.inputs import PriorityInput


def e02_result(task_id="TSK-101", criticality="CRITICAL", overdue=30):
    """Real E02 result (produced by the public engine, never mocked numbers)."""
    return PriorityEngine().evaluate(
        PriorityInput(
            task_id=task_id,
            section_id="SEC-01",
            criticality=criticality,
            overdue_days=overdue,
        )
    )


def assignment(task_id="TSK-101", unscheduled=True, priority=None):
    return TaskAssignment(
        task_id=task_id,
        unscheduled=unscheduled,
        priority=priority if unscheduled else None,
    )


def solution(plan_id="PLAN-A", assignments=None, blocks=None, delay=0.0):
    return CandidateSolution(
        plan_id=plan_id,
        assignments=assignments or [],
        blocks=blocks or [],
        total_train_delay_minutes=delay,
    )


def block(window_id="WIN-1", bundle=0.0, overrun=0.0):
    return BlockActivation(window_id=window_id, bundle_bonus=bundle, overrun_risk=overrun)


# ---------------------------------------------------------------------------
# Basic integration (§20 A)
# ---------------------------------------------------------------------------


def test_valid_e02_priority_result_is_accepted():
    evaluator = ObjectiveEvaluator()
    breakdown = evaluator.evaluate(
        solution(assignments=[assignment(priority=e02_result())])
    )
    assert breakdown.priority_contributions[0].task_id == "TSK-101"


# ---------------------------------------------------------------------------
# Score propagation (§20 B) — exact authoritative formula
# ---------------------------------------------------------------------------


def test_priority_contribution_is_beta_times_score():
    score = e02_result(criticality="HIGH", overdue=15).score
    beta = 4.0  # default
    breakdown = ObjectiveEvaluator().evaluate(
        solution(assignments=[assignment(priority=e02_result(criticality="HIGH", overdue=15))])
    )
    assert breakdown.priority_component == pytest.approx(beta * score, abs=1e-9)
    assert breakdown.priority_contributions[0].contribution == pytest.approx(beta * score, abs=1e-9)


def test_beta_multiplies_each_unscheduled_task_and_sums():
    p1 = e02_result("TSK-1", "LOW", 0)
    p2 = e02_result("TSK-2", "MEDIUM", 10)
    breakdown = ObjectiveEvaluator().evaluate(
        solution(assignments=[
            assignment("TSK-1", True, p1),
            assignment("TSK-2", True, p2),
        ])
    )
    expected = 4.0 * p1.score + 4.0 * p2.score
    assert breakdown.priority_component == pytest.approx(expected, abs=1e-9)


def test_scheduled_tasks_contribute_zero_to_priority_term():
    p = e02_result()
    breakdown = ObjectiveEvaluator().evaluate(
        solution(assignments=[assignment("TSK-1", False, p)])
    )
    assert breakdown.priority_component == pytest.approx(0.0)
    assert breakdown.priority_contributions == []


def test_total_objective_is_exact_sum_of_signed_components():
    p1 = e02_result("TSK-1", "CRITICAL", 45)
    p2 = e02_result("TSK-2", "HIGH", 12)
    sol = solution(
        assignments=[assignment("TSK-1", True, p1), assignment("TSK-2", True, p2)],
        blocks=[block("W1", bundle=2.0, overrun=0.25), block("W2", bundle=0.0, overrun=0.5)],
        delay=37.5,
    )
    breakdown = ObjectiveEvaluator().evaluate(sol)
    manual = (
        5.0 * 37.5          # α·delay
        + 4.0 * p1.score    # β·p1
        + 4.0 * p2.score    # β·p2
        + 1.0 * 2           # γ·blocks
        + 2.0 * (0.25 + 0.5)  # δ·overruns
        - 1.0 * 2.0         # ε·bundle (reward subtracted)
    )
    assert breakdown.total_objective == pytest.approx(manual, abs=1e-9)


# ---------------------------------------------------------------------------
# Boundary values (§20 C, D, E)
# ---------------------------------------------------------------------------


def test_zero_priority_score_gives_zero_contribution():
    # Explicit zero: the only configured factor (criticality) is zero-weighted
    # and every optional factor is absent, so the weighted mean is exactly 0.0.
    engine = PriorityEngine(PriorityEngineConfig(criticality_weight=0.0))
    zero_result = engine.evaluate(
        PriorityInput(task_id="TSK-Z", section_id="SEC-01", criticality="LOW", overdue_days=0)
    )
    assert zero_result.score == pytest.approx(0.0)
    breakdown = ObjectiveEvaluator().evaluate(
        solution(assignments=[assignment("TSK-Z", True, zero_result)])
    )
    assert breakdown.priority_component == pytest.approx(0.0)


def test_maximum_priority_score_gives_beta_contribution():
    p = e02_result("TSK-MAX", "CRITICAL", 45)
    assert p.score == pytest.approx(1.0)  # all present factors saturate
    breakdown = ObjectiveEvaluator().evaluate(
        solution(assignments=[assignment("TSK-MAX", True, p)])
    )
    assert breakdown.priority_component == pytest.approx(4.0)  # β=4 × 1.0


def test_beta_zero_removes_priority_influence():
    evaluator = ObjectiveEvaluator(OptimizationConfig(unscheduled_priority_weight=0.0))
    breakdown = evaluator.evaluate(
        solution(assignments=[assignment("TSK-1", True, e02_result())])
    )
    assert breakdown.priority_component == pytest.approx(0.0)
    assert breakdown.total_objective == pytest.approx(0.0)  # nothing else present


def test_beta_scaling_is_linear():
    base = solution(assignments=[assignment("TSK-1", True, e02_result())])
    half = ObjectiveEvaluator(OptimizationConfig(unscheduled_priority_weight=2.0)).evaluate(base)
    full = ObjectiveEvaluator(OptimizationConfig(unscheduled_priority_weight=4.0)).evaluate(base)
    assert full.priority_component == pytest.approx(2.0 * half.priority_component, abs=1e-12)


# ---------------------------------------------------------------------------
# Other §17.5 terms + ranking
# ---------------------------------------------------------------------------


def test_delay_block_overrun_and_bundling_terms():
    sol = solution(
        blocks=[block("W1", bundle=3.0, overrun=1.0), block("W2", bundle=1.0, overrun=0.0)],
        delay=10.0,
    )
    breakdown = ObjectiveEvaluator().evaluate(sol)
    assert breakdown.train_delay_component == pytest.approx(50.0)   # 5 × 10
    assert breakdown.block_count_component == pytest.approx(2.0)    # 1 × 2 blocks
    assert breakdown.overrun_risk_component == pytest.approx(2.0)   # 2 × 1.0
    assert breakdown.bundling_component == pytest.approx(4.0)       # 1 × 4.0
    assert breakdown.other_objective_components["bundling"] == pytest.approx(4.0)


def test_rank_candidates_lower_objective_first_with_neutral_tiebreak():
    evaluator = ObjectiveEvaluator()
    high = evaluator.evaluate(solution("PLAN-B", delay=100.0))
    low = evaluator.evaluate(solution("PLAN-A", delay=10.0))
    tie1 = evaluator.evaluate(solution("PLAN-Y", delay=42.0))
    tie2 = evaluator.evaluate(solution("PLAN-X", delay=42.0))
    ranked = rank_candidates([high, low, tie1, tie2])
    assert [b.plan_id for b in ranked] == ["PLAN-A", "PLAN-X", "PLAN-Y", "PLAN-B"]


# ---------------------------------------------------------------------------
# Determinism (§20 G)
# ---------------------------------------------------------------------------


def test_identical_solution_evaluates_identically():
    evaluator = ObjectiveEvaluator()
    sol = solution(
        assignments=[assignment("TSK-1", True, e02_result())],
        blocks=[block("W1", bundle=1.0, overrun=0.5)],
        delay=15.0,
    )
    first = evaluator.evaluate(sol)
    second = evaluator.evaluate(
        solution(
            assignments=[assignment("TSK-1", True, e02_result())],
            blocks=[block("W1", bundle=1.0, overrun=0.5)],
            delay=15.0,
        )
    )
    assert first.model_dump() == second.model_dump()


def test_evaluator_reuses_configuration_immutably():
    evaluator = ObjectiveEvaluator()
    cfg_before = evaluator.config.model_dump()
    evaluator.evaluate(solution(assignments=[assignment("TSK-1", True, e02_result())]))
    assert evaluator.config.model_dump() == cfg_before
