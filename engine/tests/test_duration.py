"""Tests — HARD rule: block duration validity (RAILMIND.HARD.BLOCK_DURATION)."""

import pytest
from pydantic import ValidationError

from engine.constraints.hard.duration import BlockDurationRule
from engine.models.context import ConstraintContext
from engine.models.inputs import CandidateBlock, DurationEstimate, TaskRequirement, TimeInterval

from engine.tests.helpers import t, t_next


def make_block(minutes: int, start=None) -> CandidateBlock:
    start = start or t(21)
    from datetime import timedelta

    end = start + timedelta(minutes=minutes)
    return CandidateBlock(section_id="SEC-01", interval=TimeInterval(start=start, end=end))


def make_task(task_id="TSK-101", expected=60, maximum=90) -> TaskRequirement:
    return TaskRequirement(
        task_id=task_id,
        section_id="SEC-01",
        department="Engineering",
        duration=DurationEstimate(expected=expected, minimum=max(0, expected - 15), maximum=maximum),
        crew_units_required=0,
    )


def make_context(block, tasks) -> ConstraintContext:
    return ConstraintContext(candidate_block=block, tasks=tasks)


def test_valid_duration_passes_with_slack_evidence():
    rule = BlockDurationRule()
    # 60 min maintenance in a 90 min block → PASS
    result = rule.evaluate(make_context(make_block(90), [make_task(expected=60)]))
    assert result.status == "PASS"
    assert result.violation_degree is None
    assert any("slack" in e.description.lower() for e in result.evidence) or result.evidence


def test_zero_duration_block_fails():
    rule = BlockDurationRule()
    block = CandidateBlock(
        section_id="SEC-01", interval=TimeInterval(start=t(21), end=t(21))
    )
    result = rule.evaluate(make_context(block, [make_task()]))
    assert result.status == "FAIL"
    assert result.severity.value == "CRITICAL"


def test_negative_duration_block_fails():
    rule = BlockDurationRule()
    # end before start → negative duration
    block = CandidateBlock(
        section_id="SEC-01", interval=TimeInterval(start=t(23), end=t(21))
    )
    result = rule.evaluate(make_context(block, [make_task()]))
    assert result.status == "FAIL"


def test_duration_exceeding_block_fails_with_deficit_evidence():
    rule = BlockDurationRule()
    # 120 min maintenance in a 90 min block → FAIL
    result = rule.evaluate(make_context(make_block(90), [make_task(expected=120, maximum=130)]))
    assert result.status == "FAIL"
    assert result.violation_degree == 30.0
    assert any("deficit" in result.explanation.lower() for _ in [0])


def test_sum_of_multiple_tasks_must_fit():
    rule = BlockDurationRule()
    result = rule.evaluate(
        make_context(make_block(90), [make_task("TSK-101", expected=50), make_task("TSK-102", expected=50)])
    )
    assert result.status == "FAIL"  # 100 > 90
    assert result.violation_degree == 10.0


def test_block_without_tasks_fails():
    rule = BlockDurationRule()
    result = rule.evaluate(make_context(make_block(90), []))
    assert result.status == "FAIL"
    assert "no maintenance tasks" in result.message.lower()


def test_naive_datetime_rejected_at_model_boundary():
    from datetime import datetime

    with pytest.raises(ValidationError):
        CandidateBlock(
            section_id="SEC-01",
            interval=TimeInterval(start=datetime(2026, 9, 14, 21), end=t_next(1)),
        )
