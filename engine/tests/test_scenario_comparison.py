"""Tests — E04 scenario comparison: the §28 test matrix + §29 invariants.

Every E02/E03 input in these tests is REAL (public engines) unless a test
deliberately forges a value to prove verbatim propagation.
"""

import math

import pytest
from pydantic import ValidationError

from engine.optimization.configuration import OptimizationConfig
from engine.optimization.evaluation import ObjectiveEvaluator
from engine.optimization.inputs import BlockActivation, CandidateSolution, TaskAssignment
from engine.optimization.result import ObjectiveBreakdown
from engine.priority.engine import PriorityEngine
from engine.priority.inputs import PriorityInput
from engine.scenario.comparison import ScenarioComparator, evaluate_candidates
from engine.scenario.inputs import ScenarioCandidate
from engine.scenario.result import ScenarioComparison


def e02_result(task_id="TSK-101", criticality="CRITICAL", overdue=30):
    return PriorityEngine().evaluate(
        PriorityInput(
            task_id=task_id,
            section_id="SEC-01",
            criticality=criticality,
            overdue_days=overdue,
        )
    )


def solution(plan_id="PLAN-A", delay=0.0, blocks=None, assignments=None):
    return CandidateSolution(
        plan_id=plan_id,
        assignments=assignments or [],
        blocks=blocks or [],
        total_train_delay_minutes=delay,
    )


def block(window_id="WIN-1", bundle=0.0, overrun=0.0):
    return BlockActivation(window_id=window_id, bundle_bonus=bundle, overrun_risk=overrun)


def candidate(candidate_id="PLAN-A", objective_total=10.0, delay=None, plan_id=None):
    """A candidate with a hand-set objective total (for pure ranking tests)."""
    breakdown = ObjectiveBreakdown(
        plan_id=plan_id or candidate_id,
        train_delay_component=objective_total,
        priority_component=0.0,
        block_count_component=0.0,
        overrun_risk_component=0.0,
        bundling_component=0.0,
        total_objective=objective_total,
    )
    return ScenarioCandidate(
        candidate_id=candidate_id,
        solution=solution(plan_id=plan_id or candidate_id, delay=delay or 0.0),
        objective=breakdown,
    )


# ---------------------------------------------------------------------------
# Test 1 — Empty candidate set
# ---------------------------------------------------------------------------


def test_empty_candidate_set_is_a_clear_error():
    with pytest.raises(ValueError, match="requires at least one candidate"):
        ScenarioComparator().compare([])


# ---------------------------------------------------------------------------
# Test 2 — Single candidate
# ---------------------------------------------------------------------------


def test_single_candidate_is_rank_1_and_selected():
    comparison = ScenarioComparator().compare([candidate("ONLY", 42.0)])
    assert len(comparison.ranked) == 1
    assert comparison.ranked[0].rank == 1
    assert comparison.selected_candidate_id == "ONLY"
    assert comparison.ranked[0].objective_delta_from_best == pytest.approx(0.0)
    assert comparison.summary.runner_up_candidate_id == ""
    assert "only candidate" in comparison.summary.statement


# ---------------------------------------------------------------------------
# Tests 3-4 — Two and multiple candidates: lower objective wins, full order
# ---------------------------------------------------------------------------


def test_two_candidates_lower_objective_wins():
    comparison = ScenarioComparator().compare(
        [candidate("EXPENSIVE", 35.8), candidate("CHEAP", 31.4)]
    )
    assert comparison.selected_candidate_id == "CHEAP"
    assert [r.candidate_id for r in comparison.ranked] == ["CHEAP", "EXPENSIVE"]
    assert [r.rank for r in comparison.ranked] == [1, 2]


def test_multiple_candidates_full_deterministic_ordering():
    comparison = ScenarioComparator().compare(
        [
            candidate("P-4", 44.0),
            candidate("P-1", 11.0),
            candidate("P-3", 33.0),
            candidate("P-2", 22.0),
            candidate("P-5", 55.0),
        ]
    )
    assert [r.candidate_id for r in comparison.ranked] == [
        "P-1", "P-2", "P-3", "P-4", "P-5",
    ]
    assert [r.rank for r in comparison.ranked] == [1, 2, 3, 4, 5]
    assert comparison.selected_candidate_id == "P-1"


# ---------------------------------------------------------------------------
# Test 5 — Exact objective tie: neutral stable identifier ordering
# ---------------------------------------------------------------------------


def test_exact_tie_resolves_by_ascending_candidate_id():
    comparison = ScenarioComparator().compare(
        [candidate("PLAN-B", 20.0), candidate("PLAN-A", 20.0), candidate("PLAN-C", 20.0)]
    )
    assert [r.candidate_id for r in comparison.ranked] == ["PLAN-A", "PLAN-B", "PLAN-C"]
    assert comparison.selected_candidate_id == "PLAN-A"
    # All ties share the best delta.
    assert all(r.objective_delta_from_best == pytest.approx(0.0) for r in comparison.ranked)


# ---------------------------------------------------------------------------
# Test 6 — Duplicate IDs
# ---------------------------------------------------------------------------


def test_duplicate_candidate_ids_are_rejected():
    with pytest.raises(ValueError, match="duplicate candidate_id"):
        ScenarioComparator().compare(
            [candidate("PLAN-A", 10.0), candidate("PLAN-A", 20.0)]
        )


# ---------------------------------------------------------------------------
# Tests 7-9 — NaN / ±Infinity rejection (E04 §11 boundary defense)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_total_objective_rejected_loudly(bad):
    with pytest.raises(ValueError, match="must be finite"):
        ScenarioComparator().compare(
            [candidate("OK", 10.0), candidate("BROKEN", bad)]
        )


@pytest.mark.parametrize("field", [
    "train_delay_component",
    "priority_component",
    "block_count_component",
    "overrun_risk_component",
    "bundling_component",
])
def test_nonfinite_objective_component_rejected(field):
    component_kwargs = {
        "train_delay_component": 0.0,
        "priority_component": 0.0,
        "block_count_component": 0.0,
        "overrun_risk_component": 0.0,
        "bundling_component": 0.0,
    }
    component_kwargs[field] = float("nan")
    breakdown = ObjectiveBreakdown(
        plan_id="BROKEN",
        total_objective=1.0,
        **component_kwargs,
    )
    with pytest.raises(ValueError, match="must be finite"):
        ScenarioComparator().compare([candidate("OK", 10.0), ScenarioCandidate(
            candidate_id="BROKEN", solution=solution("BROKEN"), objective=breakdown
        )])


# ---------------------------------------------------------------------------
# Test 10 — Objective breakdown preservation (never reduced to a float)
# ---------------------------------------------------------------------------


def test_full_e03_breakdown_survives_ranking():
    sol = solution(
        "PLAN-FULL",
        delay=12.0,
        blocks=[block("W1", bundle=2.0, overrun=0.25)],
    )
    breakdown = ObjectiveEvaluator().evaluate(sol)
    comparison = ScenarioComparator().compare(
        [ScenarioCandidate(candidate_id="PLAN-FULL", solution=sol, objective=breakdown)]
    )
    entry = comparison.ranked[0]
    assert entry.objective_breakdown.model_dump() == breakdown.model_dump()
    assert entry.total_objective == pytest.approx(breakdown.total_objective)
    assert entry.solution.model_dump() == sol.model_dump()


# ---------------------------------------------------------------------------
# Tests 11-12 — Priority provenance through E02→E03→E04; never recalculated
# ---------------------------------------------------------------------------


def _two_plan_chain():
    """Plan A leaves a high-priority task unscheduled; Plan B schedules it."""
    priority = e02_result("TSK-1", "CRITICAL", 45)
    plan_a = solution(
        "PLAN-A",
        assignments=[TaskAssignment(task_id="TSK-1", unscheduled=True, priority=priority)],
    )
    plan_b = solution(
        "PLAN-B",
        assignments=[TaskAssignment(task_id="TSK-1", unscheduled=False)],
    )
    return priority, plan_a, plan_b


def test_e02_provenance_survives_through_e03_to_e04():
    priority, plan_a, plan_b = _two_plan_chain()
    comparison = evaluate_candidates([plan_a, plan_b])
    loser = next(r for r in comparison.ranked if r.candidate_id == "PLAN-A")
    contributions = loser.objective_breakdown.priority_contributions
    assert contributions[0].priority_model_id == priority.priority_model_id
    assert contributions[0].priority_model_version == priority.priority_model_version
    # The winner scheduled the task: no β cost, no fabricated provenance.
    winner = comparison.best()
    assert winner.candidate_id == "PLAN-B"
    assert winner.objective_breakdown.priority_contributions == []


def test_e04_never_recalculates_priority():
    # Hand-crafted priority score flows verbatim into the E04-ranked breakdown.
    from engine.priority.result import PriorityResult

    forged = PriorityResult(task_id="TSK-H", score=0.123456, priority_class="LOW")
    sol = solution(
        "PLAN-FORGE",
        assignments=[TaskAssignment(task_id="TSK-H", unscheduled=True, priority=forged)],
    )
    comparison = evaluate_candidates([sol])
    contribution = comparison.ranked[0].objective_breakdown.priority_contributions[0]
    assert contribution.priority_score == pytest.approx(0.123456)
    assert contribution.contribution == pytest.approx(4.0 * 0.123456)


# ---------------------------------------------------------------------------
# Test 13 — Input immutability
# ---------------------------------------------------------------------------


def test_input_candidates_are_never_mutated():
    priority = e02_result("TSK-1")
    sols = [
        solution(
            "PLAN-A",
            delay=10.0,
            blocks=[block("W1", bundle=1.0, overrun=0.5)],
            assignments=[TaskAssignment(task_id="TSK-1", unscheduled=True, priority=priority)],
        ),
        solution("PLAN-B", delay=20.0),
        solution("PLAN-C", delay=30.0),
    ]
    candidates = [
        ScenarioCandidate(
            candidate_id=s.plan_id,
            solution=s,
            objective=ObjectiveEvaluator().evaluate(s),
        )
        for s in sols
    ]
    before_solutions = [s.model_dump() for s in sols]
    before_candidates = [c.model_dump() for c in candidates]
    before_objectives = [c.objective.model_dump() for c in candidates]

    comparison = ScenarioComparator().compare(candidates)

    # Nothing changed anywhere: solutions, candidates and breakdowns are all
    # byte-identical after ranking (frozen models; comparator never mutates).
    assert [s.model_dump() for s in sols] == before_solutions
    assert [c.model_dump() for c in candidates] == before_candidates
    assert [c.objective.model_dump() for c in candidates] == before_objectives
    assert len(comparison.ranked) == 3


# ---------------------------------------------------------------------------
# Tests 14-15 — Determinism and permutation invariance
# ---------------------------------------------------------------------------


def _fixture_candidates():
    return [
        candidate("PLAN-C", 30.0),
        candidate("PLAN-A", 10.0),
        candidate("PLAN-E", 50.0),
        candidate("PLAN-B", 10.0),  # ties with PLAN-A → id order
        candidate("PLAN-D", 40.0),
    ]


def test_identical_inputs_produce_identical_results():
    first = ScenarioComparator().compare(_fixture_candidates())
    second = ScenarioComparator().compare(_fixture_candidates())
    assert first.model_dump() == second.model_dump()


def test_input_order_permutation_does_not_change_result():
    import itertools

    base = ScenarioComparator().compare(_fixture_candidates()).model_dump()
    perms = list(itertools.permutations(range(5)))[:12]  # 12 of 120 orders
    for perm in perms:
        shuffled = [_fixture_candidates()[i] for i in perm]
        assert ScenarioComparator().compare(shuffled).model_dump() == base


# ---------------------------------------------------------------------------
# Test 16 — Objective delta: exact mathematics
# ---------------------------------------------------------------------------


def test_objective_delta_from_best_is_exact():
    comparison = ScenarioComparator().compare(
        [candidate("BEST", 10.0), candidate("MID", 10.0 + 2.5), candidate("WORST", 10.0 + 7.5)]
    )
    assert comparison.ranked[0].objective_delta_from_best == pytest.approx(0.0)
    assert comparison.ranked[1].objective_delta_from_best == pytest.approx(2.5)
    assert comparison.ranked[2].objective_delta_from_best == pytest.approx(7.5)
    # Summary total delta: winner vs runner-up.
    assert comparison.summary.total_objective_delta == pytest.approx(-2.5)


# ---------------------------------------------------------------------------
# Test 17 — Feasibility policy: E04 compares objective among supplied candidates
# ---------------------------------------------------------------------------


def test_e04_has_no_feasibility_bypass_and_no_penalty_invention():
    """Structural policy test (report §6): E04 neither consumes E01 results
    nor invents infinity penalties — it ranks exactly what the caller gives."""
    comparison = ScenarioComparator().compare(
        [candidate("A", 10.0), candidate("B", 20.0)]
    )
    # The only lever on ranking is the objective value: no feasibility field
    # exists anywhere in the E04 input model.
    fields = set(ScenarioCandidate.model_fields)
    assert not any("feasib" in f or "violat" in f for f in fields)
    # Lower objective wins — there is no hidden penalty mechanism.
    assert comparison.selected_candidate_id == "A"


# ---------------------------------------------------------------------------
# Test 18 — Large candidate set (deterministic, no performance cliff)
# ---------------------------------------------------------------------------


def test_large_candidate_set_ranks_correctly():
    sols = [
        solution(f"PLAN-{i:03d}", delay=float(i)) for i in range(200)
    ]
    comparison = evaluate_candidates(sols)
    assert len(comparison.ranked) == 200
    assert comparison.selected_candidate_id == "PLAN-000"
    totals = [r.total_objective for r in comparison.ranked]
    assert totals == sorted(totals)
    assert [r.rank for r in comparison.ranked] == list(range(1, 201))
    # Deltas consistent with the best.
    best = totals[0]
    assert all(
        r.objective_delta_from_best == pytest.approx(t - best)
        for r, t in zip(comparison.ranked, totals)
    )


# ---------------------------------------------------------------------------
# Test 19 — Tiny floating-point differences remain correctly ordered
# ---------------------------------------------------------------------------


def test_boundary_float_differences_stay_ordered():
    tiny = 1e-9
    comparison = ScenarioComparator().compare(
        [candidate("PLAN-B", 10.0 + tiny), candidate("PLAN-A", 10.0)]
    )
    assert [r.candidate_id for r in comparison.ranked] == ["PLAN-A", "PLAN-B"]
    assert comparison.ranked[1].objective_delta_from_best == pytest.approx(tiny)


# ---------------------------------------------------------------------------
# Test 20 — Serialization round-trip (project model conventions)
# ---------------------------------------------------------------------------


def test_comparison_is_serializable_roundtrip():
    priority, plan_a, plan_b = _two_plan_chain()
    comparison = evaluate_candidates([plan_a, plan_b])
    restored = ScenarioComparison.model_validate(comparison.model_dump())
    assert restored.model_dump() == comparison.model_dump()


# ---------------------------------------------------------------------------
# §29 Property-style invariants (parametrized, no property dependency)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("a,b", [(5.0, 9.0), (0.0, 0.5), (100.0, 100.5)])
def test_monotonic_ordering(a, b):
    comparison = ScenarioComparator().compare([candidate("B", b), candidate("A", a)])
    ranks = {r.candidate_id: r.rank for r in comparison.ranked}
    if a < b:
        assert ranks["A"] < ranks["B"]
    else:
        assert ranks["A"] <= ranks["B"]  # ties → id order; A still first


def test_equal_value_distinct_candidates_are_ordered_stably():
    first = ScenarioComparator().compare([candidate("X", 7.0), candidate("Y", 7.0)])
    second = ScenarioComparator().compare([candidate("Y", 7.0), candidate("X", 7.0)])
    assert [r.candidate_id for r in first.ranked] == ["X", "Y"]
    assert [r.candidate_id for r in second.ranked] == ["X", "Y"]


def test_real_solution_comparison_matches_manual_e03_math():
    """End-to-end: evaluate_candidates must equal manual E03 evaluation."""
    priority, plan_a, plan_b = _two_plan_chain()
    comparison = evaluate_candidates([plan_a, plan_b])
    evaluator = ObjectiveEvaluator()
    manual_a = evaluator.evaluate(plan_a)
    manual_b = evaluator.evaluate(plan_b)
    by_id = {r.candidate_id: r for r in comparison.ranked}
    assert by_id["PLAN-A"].total_objective == pytest.approx(manual_a.total_objective)
    assert by_id["PLAN-B"].total_objective == pytest.approx(manual_b.total_objective)
    assert comparison.selected_candidate_id == "PLAN-B"  # schedules the task


def test_evaluate_candidates_respects_custom_beta():
    priority, plan_a, plan_b = _two_plan_chain()
    # β=0: priority no longer penalizes leaving the task unscheduled; both
    # plans are identical → tie broken by ascending candidate_id.
    comparison = evaluate_candidates(
        [plan_a, plan_b], config=OptimizationConfig(unscheduled_priority_weight=0.0)
    )
    assert comparison.ranked[0].total_objective == pytest.approx(0.0)
    assert comparison.ranked[1].total_objective == pytest.approx(0.0)
    assert comparison.selected_candidate_id == "PLAN-A"  # neutral tie-break
