"""Tests — HARD rule: planning horizon containment (inclusive boundaries)."""

from engine.constraints.hard.planning_horizon import PlanningHorizonRule
from engine.models.context import ConstraintContext
from engine.models.inputs import CandidateBlock, TimeInterval

from engine.tests.helpers import t, t_next


def evaluate(block_interval, horizon_interval) -> object:
    context = ConstraintContext(
        candidate_block=CandidateBlock(section_id="SEC-01", interval=block_interval),
        planning_horizon=horizon_interval,
    )
    return PlanningHorizonRule().evaluate(context)


def test_inside_horizon_passes():
    horizon = TimeInterval(start=t(0), end=t_next(0))  # 72h horizon
    result = evaluate(TimeInterval(start=t(21), end=t(23)), horizon)
    assert result.status == "PASS"


def test_starts_at_horizon_boundary_passes():
    horizon = TimeInterval(start=t(21), end=t_next(0))
    result = evaluate(TimeInterval(start=t(21), end=t(23)), horizon)
    assert result.status == "PASS"


def test_ends_at_horizon_boundary_passes():
    horizon = TimeInterval(start=t(0), end=t(23))
    result = evaluate(TimeInterval(start=t(21), end=t(23)), horizon)
    assert result.status == "PASS"


def test_starts_before_horizon_fails():
    horizon = TimeInterval(start=t(22), end=t_next(0))
    result = evaluate(TimeInterval(start=t(21), end=t(23)), horizon)
    assert result.status == "FAIL"
    assert result.violation_degree == 60.0


def test_ends_after_horizon_fails():
    horizon = TimeInterval(start=t(0), end=t(22))
    result = evaluate(TimeInterval(start=t(21), end=t(23)), horizon)
    assert result.status == "FAIL"
    assert result.violation_degree == 60.0


def test_block_entirely_outside_horizon_fails():
    horizon = TimeInterval(start=t(0), end=t(12))
    result = evaluate(TimeInterval(start=t(21), end=t(23)), horizon)
    assert result.status == "FAIL"


def test_no_horizon_configured_passes_with_info():
    context = ConstraintContext(
        candidate_block=CandidateBlock(section_id="SEC-01", interval=TimeInterval(start=t(21), end=t(23))),
        planning_horizon=None,
    )
    result = PlanningHorizonRule().evaluate(context)
    assert result.status == "PASS"
    assert result.severity.value == "INFO"
    assert "disabled" in result.explanation
