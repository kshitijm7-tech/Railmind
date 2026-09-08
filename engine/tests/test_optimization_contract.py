"""E02→E03 contract tests (§21): the boundary that must never erode.

These tests make it difficult for future code to accidentally reimplement
priority inside E03: every test constructs a REAL E02 result through the
public PriorityEngine and verifies E03 consumes it verbatim.
"""

import math

import pytest
from pydantic import ValidationError

from engine.optimization.configuration import OptimizationConfig
from engine.optimization.evaluation import ObjectiveEvaluator, _validate_priority_score
from engine.optimization.inputs import BlockActivation, CandidateSolution, TaskAssignment
from engine.optimization.result import ObjectiveBreakdown, PriorityComponent
from engine.priority.configuration import PriorityEngineConfig
from engine.priority.engine import PriorityEngine
from engine.priority.inputs import PriorityInput
from engine.priority.result import FactorScore, PriorityResult
from engine._version import (
    ENGINE_VERSION,
    OPTIMIZATION_MODEL_ID,
    OPTIMIZATION_MODEL_VERSION,
    PRIORITY_MODEL_ID,
    PRIORITY_MODEL_VERSION,
)


def e02_result(task_id="TSK-101", criticality="CRITICAL", overdue=30):
    """A REAL E02 result produced by the public engine (never mocked)."""
    return PriorityEngine().evaluate(
        PriorityInput(
            task_id=task_id,
            section_id="SEC-01",
            criticality=criticality,
            overdue_days=overdue,
        )
    )


def unscheduled(task_id="TSK-101", priority=None):
    return TaskAssignment(
        task_id=task_id, unscheduled=True, priority=priority or e02_result(task_id)
    )


def solution(plan_id="PLAN-A", assignments=None):
    return CandidateSolution(plan_id=plan_id, assignments=assignments or [])


# ---------------------------------------------------------------------------
# §20 L — Missing priority: fail clearly, never a silent zero
# ---------------------------------------------------------------------------


def test_unscheduled_task_without_priority_result_is_a_contract_error():
    with pytest.raises(ValidationError) as exc:
        TaskAssignment(task_id="TSK-9", unscheduled=True, priority=None)
    assert "requires its E02 PriorityResult" in str(exc.value)


def test_missing_priority_is_never_substituted_with_zero():
    # The error must be raised at the boundary — not silently converted to a
    # 0.0 priority contribution inside the evaluator.
    with pytest.raises(ValidationError):
        CandidateSolution(
            plan_id="PLAN-A",
            assignments=[TaskAssignment(task_id="TSK-9", unscheduled=True)],
        )


def test_scheduled_task_may_omit_priority():
    assignment = TaskAssignment(task_id="TSK-9", unscheduled=False)
    assert assignment.priority is None


# ---------------------------------------------------------------------------
# §20 H — Factor propagation: contributions carried verbatim, never recomputed
# ---------------------------------------------------------------------------


def test_factor_contributions_are_carried_verbatim_from_e02():
    priority = e02_result("TSK-1", "HIGH", 20)
    breakdown = ObjectiveEvaluator().evaluate(
        solution(assignments=[unscheduled("TSK-1", priority)])
    )
    carried = breakdown.priority_contributions[0].factor_contributions
    source = {f.factor: f.contribution for f in priority.factor_scores}
    assert carried == source
    # And the sum of carried factor contributions reconciles with the E02 score.
    assert sum(carried.values()) == pytest.approx(priority.score, abs=1e-9)


def test_factor_contributions_are_not_recomputed_from_task_attributes():
    # Build a PriorityResult whose factor list is deliberately inconsistent
    # with any "natural" recomputation from task attributes — E03 must still
    # carry it verbatim (auditability over assumptions, §9).
    forged = PriorityResult(
        task_id="TSK-F",
        score=0.42,
        priority_class="MEDIUM",
        factor_scores=[
            FactorScore(
                factor="criticality",
                normalized_score=0.7,
                weight=0.6,
                contribution=0.42,
            )
        ],
    )
    breakdown = ObjectiveEvaluator().evaluate(
        solution(assignments=[unscheduled("TSK-F", forged)])
    )
    component = breakdown.priority_contributions[0]
    assert component.priority_score == pytest.approx(0.42)
    assert component.contribution == pytest.approx(4.0 * 0.42)
    assert component.factor_contributions == {"criticality": 0.42}


def test_e02_score_is_never_recomputed_by_e03():
    # If E03 rebuilt priority from raw attributes, a hand-crafted score would
    # differ from the "natural" value. The breakdown must report exactly the
    # score the E02 result carries.
    priority = PriorityResult(
        task_id="TSK-H",
        score=0.123456,
        priority_class="LOW",
    )
    breakdown = ObjectiveEvaluator().evaluate(
        solution(assignments=[unscheduled("TSK-H", priority)])
    )
    assert breakdown.priority_contributions[0].priority_score == pytest.approx(0.123456)


# ---------------------------------------------------------------------------
# §20 J — Provenance: E02 lineage retained, E03 lineage explicit
# ---------------------------------------------------------------------------


def test_e02_provenance_is_retained_not_overwritten():
    priority = e02_result("TSK-P", "CRITICAL", 45)
    breakdown = ObjectiveEvaluator().evaluate(
        solution(assignments=[unscheduled("TSK-P", priority)])
    )
    component = breakdown.priority_contributions[0]
    assert component.priority_model_id == priority.priority_model_id
    assert component.priority_model_id == PRIORITY_MODEL_ID
    assert component.priority_model_version == priority.priority_model_version
    assert component.priority_model_version == PRIORITY_MODEL_VERSION


def test_breakdown_carries_distinct_e03_and_e02_lineage():
    priority = e02_result()
    breakdown = ObjectiveEvaluator().evaluate(
        solution(assignments=[unscheduled(priority=priority)])
    )
    assert breakdown.optimization_model_id == OPTIMIZATION_MODEL_ID
    assert breakdown.optimization_model_version == OPTIMIZATION_MODEL_VERSION
    assert breakdown.engine_version == ENGINE_VERSION
    # The E02 identity remains distinct from the E03 identity.
    assert breakdown.priority_contributions[0].priority_model_id != breakdown.optimization_model_id


# ---------------------------------------------------------------------------
# §21 — Boundary shape: PriorityResult → E03 objective input → evaluation
# ---------------------------------------------------------------------------


def test_public_e02_result_flows_directly_into_objective_input():
    """The intended integration: public engine → public result → E03 input."""
    priority = PriorityEngine().evaluate(
        PriorityInput(
            task_id="TSK-FLOW",
            section_id="SEC-01",
            criticality="CRITICAL",
            overdue_days=45,
        )
    )
    assignment = TaskAssignment(task_id="TSK-FLOW", unscheduled=True, priority=priority)
    breakdown = ObjectiveEvaluator().evaluate(CandidateSolution(plan_id="P", assignments=[assignment]))
    assert breakdown.priority_component == pytest.approx(4.0 * priority.score, abs=1e-9)


def test_breakdown_is_serializable_roundtrip():
    priority = e02_result()
    breakdown = ObjectiveEvaluator().evaluate(solution(assignments=[unscheduled(priority=priority)]))
    restored = ObjectiveBreakdown.model_validate(breakdown.model_dump())
    assert restored.model_dump() == breakdown.model_dump()


# ---------------------------------------------------------------------------
# §20 K — Feasibility separation: E03 cannot relax E01
# ---------------------------------------------------------------------------


def test_priority_component_contains_no_feasibility_information():
    """The objective breakdown exposes cost only — no feasibility override."""
    breakdown = ObjectiveEvaluator().evaluate(solution(assignments=[unscheduled()]))
    dump = breakdown.model_dump()
    assert not any("feasib" in key for key in dump)
    assert not any("violat" in key for key in dump)


def test_priority_does_not_bypass_hard_constraints_in_ranking():
    """Ranking operates on objective cost only; feasibility is the caller's gate.

    A plan with lower cost wins; nothing in E03 reinterprets priority as a
    licence to ignore E01's hard constraints — there is no code path that
    consumes ConstraintResult/feasibility here.
    """
    evaluator = ObjectiveEvaluator()
    expensive = evaluator.evaluate(solution("PLAN-EXPENSIVE", [unscheduled()]))
    cheap = evaluator.evaluate(solution("PLAN-CHEAP", []))
    assert cheap.total_objective < expensive.total_objective
    # The breakdown exposes no mechanism by which priority could relax a
    # constraint: the only lever on total_objective is the §17.5 formula.
    assert expensive.total_objective == pytest.approx(
        expensive.priority_component
        + expensive.train_delay_component
        + expensive.block_count_component
        + expensive.overrun_risk_component
        - expensive.bundling_component,
        abs=1e-9,
    )


# ---------------------------------------------------------------------------
# §20 M — Numerical safety at the E03 boundary
# ---------------------------------------------------------------------------


def test_nonfinite_priority_score_is_rejected_loudly():
    for bad in (float("nan"), float("inf"), -0.5, 1.5):
        forged = PriorityResult(task_id="TSK-BAD", score=bad, priority_class="LOW")
        assignment = TaskAssignment(task_id="TSK-BAD", unscheduled=True, priority=forged)
        with pytest.raises(ValueError, match=r"contract violation"):
            ObjectiveEvaluator().evaluate(CandidateSolution(plan_id="P", assignments=[assignment]))


def test_score_validation_helper_rejects_out_of_range():
    with pytest.raises(ValueError, match=r"within \[0, 1\]"):
        _validate_priority_score("TSK-X", PriorityResult(task_id="TSK-X", score=2.0, priority_class="LOW"))
    # A finite in-range score passes.
    _validate_priority_score(
        "TSK-OK", PriorityResult(task_id="TSK-OK", score=0.5, priority_class="MEDIUM")
    )


def test_nan_inputs_rejected_at_solution_boundary():
    with pytest.raises(ValidationError):
        CandidateSolution(
            plan_id="P",
            total_train_delay_minutes=float("nan"),
        )
    with pytest.raises(ValidationError):
        BlockActivation(window_id="W", bundle_bonus=float("inf"))


def test_bundle_and_overrun_are_defended_at_the_boundary():
    with pytest.raises(ValidationError):
        BlockActivation(window_id="W", overrun_risk=1.5)
    with pytest.raises(ValidationError):
        BlockActivation(window_id="W", bundle_bonus=-0.1)


# ---------------------------------------------------------------------------
# β semantics: distinct from E02 factor weights (§7)
# ---------------------------------------------------------------------------


def test_beta_is_optimization_level_not_e02_factor_weights():
    cfg = OptimizationConfig()
    # β defaults to the §17.5 value 4.0 — unrelated to E02's 0.30/0.20/... axes.
    assert cfg.unscheduled_priority_weight == pytest.approx(4.0)
    # Changing β does not touch E02's internal configuration space at all.
    assert not hasattr(cfg, "criticality_weight")
    assert not hasattr(cfg, "overdue_weight")


def test_beta_applies_after_e02_weights_have_shaped_the_score():
    """End-to-end: E02 weights → score; β scales that score in the objective."""
    priority = PriorityEngine(
        PriorityEngineConfig(criticality_weight=1.0)  # E02-internal weight
    ).evaluate(PriorityInput(task_id="T", section_id="S", criticality="CRITICAL", overdue_days=0))
    # E02 renormalizes its internal weights across present factors, producing
    # whatever score that configuration yields; β scales it verbatim.
    breakdown = ObjectiveEvaluator(
        OptimizationConfig(unscheduled_priority_weight=7.5)  # E03 β
    ).evaluate(solution("P", [unscheduled("T", priority)]))
    component = breakdown.priority_contributions[0]
    assert component.contribution == pytest.approx(7.5 * priority.score, abs=1e-9)
    assert component.beta == pytest.approx(7.5)


def test_breakdown_records_weights_actually_used():
    breakdown = ObjectiveEvaluator(OptimizationConfig(train_delay_weight=9.9)).evaluate(solution())
    assert breakdown.weights["train_delay"] == pytest.approx(9.9)
    assert breakdown.weights["unscheduled_priority"] == pytest.approx(4.0)
