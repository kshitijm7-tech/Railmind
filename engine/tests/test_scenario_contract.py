"""E04 contract tests: the architecture boundaries that must never erode.

Pins:
- E04 consumes E03 PUBLIC contracts only (no private-module reach-ins);
- dependency direction E04 → E03 → E02 (no cycles, no back-imports);
- one source of truth for the objective formula (E03) and priority (E02);
- E04 config never duplicates E03's α/β/γ/δ/ε;
- provenance chain E02 → E03 → E04 survives comparison and serialization.
"""

import inspect
import math

import pytest

import engine
from engine._version import (
    ENGINE_VERSION,
    OPTIMIZATION_MODEL_ID,
    OPTIMIZATION_MODEL_VERSION,
    PRIORITY_MODEL_ID,
    PRIORITY_MODEL_VERSION,
    SCENARIO_MODEL_ID,
    SCENARIO_MODEL_VERSION,
)
from engine.optimization.configuration import OptimizationConfig
from engine.optimization.evaluation import ObjectiveEvaluator
from engine.optimization.inputs import CandidateSolution, TaskAssignment
from engine.priority.engine import PriorityEngine
from engine.priority.inputs import PriorityInput
from engine.scenario.comparison import ScenarioComparator, evaluate_candidates
from engine.scenario.inputs import ScenarioCandidate


def e02_result(task_id="TSK-1", criticality="CRITICAL", overdue=30):
    return PriorityEngine().evaluate(
        PriorityInput(
            task_id=task_id,
            section_id="SEC-01",
            criticality=criticality,
            overdue_days=overdue,
        )
    )


def solution(plan_id="PLAN-A", delay=0.0, unscheduled_priority=None):
    assignments = []
    if unscheduled_priority is not None:
        assignments.append(
            TaskAssignment(
                task_id=unscheduled_priority.task_id,
                unscheduled=True,
                priority=unscheduled_priority,
            )
        )
    return CandidateSolution(
        plan_id=plan_id, assignments=assignments, total_train_delay_minutes=delay
    )


# ---------------------------------------------------------------------------
# Public-contract consumption: no private E03/E02 reach-ins
# ---------------------------------------------------------------------------


def test_scenario_package_imports_only_public_engine_contracts():
    import engine.scenario
    import engine.scenario.comparison
    import engine.scenario.inputs
    import engine.scenario.result

    for module in (engine.scenario, engine.scenario.comparison,
                   engine.scenario.inputs, engine.scenario.result):
        source = inspect.getsource(module)
        # Private-module reach-ins are architectural erosion.
        for token in ("from engine.optimization._", "from engine.priority._",
                      "engine.optimization.evaluation._", "engine.priority.engine._"):
            assert token not in source, f"{module.__name__} reaches into private internals: {token!r}"


def test_e04_uses_the_real_e03_evaluator_not_a_reimplementation():
    from engine.scenario import comparison

    # The delegation path is wired to E03's evaluator class itself.
    assert comparison.ObjectiveEvaluator is ObjectiveEvaluator
    # And E04's public convenience path produces the same numbers as a manual
    # E03 evaluation — proving there is exactly one formula implementation.
    priority = e02_result()
    sol = solution("PLAN-P", delay=7.0, unscheduled_priority=priority)
    via_e04 = evaluate_candidates([sol]).ranked[0].total_objective
    via_e03 = ObjectiveEvaluator().evaluate(sol).total_objective
    assert via_e04 == pytest.approx(via_e03, abs=1e-12)


def test_dependency_direction_no_back_imports():
    """E04 → E03 → E02. Nothing lower may import a higher layer."""
    import engine.optimization.evaluation
    import engine.priority.engine
    import engine.scenario.comparison

    lower_sources = "\n".join(
        inspect.getsource(m)
        for m in (engine.optimization.evaluation, engine.priority.engine)
    )
    assert "engine.scenario" not in lower_sources


# ---------------------------------------------------------------------------
# Configuration separation: E04 does not duplicate α/β/γ/δ/ε
# ---------------------------------------------------------------------------


def test_e04_exposes_no_objective_weight_duplicates():
    scenario_fields = set(ScenarioCandidate.model_fields)
    public_names = set(engine.__all__)
    for weight in ("train_delay_weight", "unscheduled_priority_weight",
                   "block_count_weight", "overrun_risk_weight",
                   "bundling_weight", "alpha", "beta", "gamma", "delta", "epsilon"):
        assert weight not in scenario_fields, f"E04 leaked objective weight {weight!r}"
        assert weight not in public_names, f"E04 leaked objective weight {weight!r}"


def test_weights_reach_e04_only_through_e03_results():
    """E04 sees weights only inside ObjectiveBreakdown.weights (E03's record)."""
    priority = e02_result()
    sol = solution("PLAN-W", delay=3.0, unscheduled_priority=priority)
    comparison = evaluate_candidates([sol])
    weights = comparison.ranked[0].objective_breakdown.weights
    assert weights == OptimizationConfig().objective_weights()


# ---------------------------------------------------------------------------
# Provenance chain E02 → E03 → E04 survives comparison and serialization
# ---------------------------------------------------------------------------


def test_full_provenance_chain_is_intact():
    priority = e02_result("TSK-CHAIN", "HIGH", 20)
    sol = solution("PLAN-CHAIN", unscheduled_priority=priority)
    comparison = evaluate_candidates([sol])
    entry = comparison.ranked[0]

    # E02 identity (inside E03's per-task contributions).
    contribution = entry.objective_breakdown.priority_contributions[0]
    assert contribution.priority_model_id == PRIORITY_MODEL_ID
    assert contribution.priority_model_version == PRIORITY_MODEL_VERSION
    # E03 identity (breakdown + ranked entry).
    assert entry.objective_breakdown.optimization_model_id == OPTIMIZATION_MODEL_ID
    assert entry.optimization_model_id == OPTIMIZATION_MODEL_ID
    assert entry.optimization_model_version == OPTIMIZATION_MODEL_VERSION
    # E04 identity (comparison + ranked entry).
    assert comparison.scenario_model_id == SCENARIO_MODEL_ID
    assert comparison.scenario_model_version == SCENARIO_MODEL_VERSION
    assert entry.scenario_model_id == SCENARIO_MODEL_ID
    assert entry.scenario_model_version == SCENARIO_MODEL_VERSION
    # Shared engine identity everywhere.
    assert entry.engine_version == ENGINE_VERSION == comparison.engine_version


def test_provenance_survives_serialization_roundtrip():
    priority = e02_result()
    sol = solution("PLAN-SER", unscheduled_priority=priority)
    comparison = evaluate_candidates([sol])
    restored = type(comparison).model_validate(comparison.model_dump())
    chain = restored.ranked[0]
    assert chain.objective_breakdown.priority_contributions[0].priority_model_id == PRIORITY_MODEL_ID
    assert chain.optimization_model_id == OPTIMIZATION_MODEL_ID
    assert chain.scenario_model_id == SCENARIO_MODEL_ID


# ---------------------------------------------------------------------------
# Summary/audit evidence integrity
# ---------------------------------------------------------------------------


def test_summary_component_deltas_are_derived_not_invented():
    priority = e02_result("TSK-D", "CRITICAL", 45)
    plan_a = solution("PLAN-A", delay=10.0)                    # schedules everything
    plan_b = solution("PLAN-B", delay=4.0, unscheduled_priority=priority)  # cheaper delay, priority cost
    comparison = evaluate_candidates([plan_a, plan_b])
    winner, loser = comparison.ranked
    summary = comparison.summary
    # Every delta equals winner − loser exactly (no invented semantics).
    for term in ("train_delay_component", "priority_component",
                 "block_count_component", "overrun_risk_component",
                 "bundling_component"):
        expected = getattr(winner.objective_breakdown, term) - getattr(loser.objective_breakdown, term)
        assert summary.component_deltas[term] == pytest.approx(expected, abs=1e-12)
    assert summary.total_objective_delta == pytest.approx(
        winner.total_objective - loser.total_objective, abs=1e-12
    )
    # wins_despite is consistent with the deltas (a real audit trail).
    for term in summary.wins_despite:
        assert summary.component_deltas[term] > 0.0
    for term in summary.deciding_components:
        assert summary.component_deltas[term] < 0.0


def test_wins_despite_is_populated_when_winner_loses_a_term():
    # PLAN-B has lower delay but leaves a CRITICAL task unscheduled — the
    # delay saving (α·5 vs α·50) outweighs the β priority cost, so PLAN-B
    # wins despite losing on the priority term. The audit trail records it.
    priority = e02_result("TSK-D", "CRITICAL", 45)
    plan_a = solution("PLAN-A", delay=10.0)
    plan_b = solution("PLAN-B", delay=1.0, unscheduled_priority=priority)
    comparison = evaluate_candidates([plan_a, plan_b])
    summary = comparison.summary
    assert summary.winner_candidate_id == "PLAN-B"
    assert "priority_component" in summary.wins_despite
    assert summary.component_deltas["priority_component"] > 0.0
    assert "train_delay_component" in summary.deciding_components


def test_single_candidate_summary_names_no_runner_up():
    comparison = evaluate_candidates([solution("SOLO", delay=5.0)])
    assert comparison.summary.runner_up_candidate_id == ""
    assert comparison.summary.component_deltas == {}
    assert comparison.summary.deciding_components == []


# ---------------------------------------------------------------------------
# Determinism & identity discipline
# ---------------------------------------------------------------------------


def test_no_randomness_or_clocks_in_scenario_modules():
    forbidden = ("datetime.now", "utcnow", "random.", "uuid.uuid4", "time.time")
    import engine.scenario.comparison
    import engine.scenario.inputs
    import engine.scenario.result

    for module in (engine.scenario.comparison, engine.scenario.inputs, engine.scenario.result):
        source = inspect.getsource(module)
        for token in forbidden:
            assert token not in source, f"{module.__name__} uses forbidden API {token!r}"


def test_engine_exports_include_e04_public_surface():
    for name in ("ScenarioCandidate", "ScenarioComparator", "ScenarioComparison",
                 "RankedCandidate", "ComparisonSummary", "evaluate_candidates"):
        assert name in engine.__all__, f"E04 export {name!r} missing from engine namespace"
    # Internal helpers stay internal.
    assert "validate_candidates" in engine.__all__  # documented public guard
    assert "_build_summary" not in engine.__all__
    assert "_OBJECTIVE_TERMS" not in engine.__all__
