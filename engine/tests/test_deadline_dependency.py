"""Tests — HARD rules: task deadline (RAILMIND.HARD.TASK_DEADLINE) and
task dependency precedence (RAILMIND.HARD.TASK_DEPENDENCY_PRECEDENCE)."""

from engine.constraints.hard.task_deadline import TaskDeadlineRule
from engine.constraints.hard.task_dependency import TaskDependencyRule
from engine.models.context import ConstraintContext
from engine.models.inputs import (
    CandidateBlock,
    DurationEstimate,
    ScheduledTaskRef,
    TaskRequirement,
    TimeInterval,
)

from engine.tests.helpers import t, t_next


def block(start=None, end=None) -> CandidateBlock:
    return CandidateBlock(
        section_id="SEC-01", interval=TimeInterval(start=start or t(21), end=end or t(23))
    )


def task(task_id="TSK-101", deadline=None, depends_on=()) -> TaskRequirement:
    return TaskRequirement(
        task_id=task_id,
        section_id="SEC-01",
        department="Engineering",
        duration=DurationEstimate(expected=60, minimum=45, maximum=90),
        latest_finish=deadline,
        depends_on=list(depends_on),
    )


# ---------------------------------------------------------------------------
# Deadline
# ---------------------------------------------------------------------------


def test_deadline_met_passes():
    context = ConstraintContext(
        candidate_block=block(), tasks=[task(deadline=t_next(2))]
    )
    result = TaskDeadlineRule().evaluate(context)
    assert result.status == "PASS"


def test_deadline_at_boundary_passes():
    # Block ends exactly at the deadline (inclusive) → PASS
    context = ConstraintContext(
        candidate_block=block(t(21), t_next(2)), tasks=[task(deadline=t_next(2))]
    )
    result = TaskDeadlineRule().evaluate(context)
    assert result.status == "PASS"


def test_deadline_missed_fails():
    context = ConstraintContext(
        candidate_block=block(), tasks=[task(deadline=t(22))]
    )
    result = TaskDeadlineRule().evaluate(context)
    assert result.status == "FAIL"
    assert result.violation_degree == 60.0


def test_earliest_deadline_is_binding():
    context = ConstraintContext(
        candidate_block=block(),
        tasks=[task("TSK-101", deadline=t_next(4)), task("TSK-102", deadline=t(22))],
    )
    result = TaskDeadlineRule().evaluate(context)
    assert result.status == "FAIL"
    assert "TSK-102" in result.explanation


def test_no_deadlines_passes():
    context = ConstraintContext(candidate_block=block(), tasks=[task(deadline=None)])
    result = TaskDeadlineRule().evaluate(context)
    assert result.status == "PASS"


# ---------------------------------------------------------------------------
# Dependency precedence
# ---------------------------------------------------------------------------


def test_predecessor_scheduled_and_finished_passes():
    # TSK-101 depends on TSK-100, scheduled 18:00–19:00 → block at 21:00 OK
    context = ConstraintContext(
        candidate_block=block(),
        tasks=[task("TSK-101", depends_on=["TSK-100"])],
        scheduled_tasks=[
            ScheduledTaskRef(task_id="TSK-100", block_id="BLK-0", interval=TimeInterval(start=t(18), end=t(19)))
        ],
    )
    result = TaskDependencyRule().evaluate(context)
    assert result.status == "PASS"


def test_predecessor_ends_after_block_starts_fails():
    # Predecessor runs 21:30–22:30, candidate block starts 21:00 → FAIL
    context = ConstraintContext(
        candidate_block=block(),
        tasks=[task("TSK-101", depends_on=["TSK-100"])],
        scheduled_tasks=[
            ScheduledTaskRef(task_id="TSK-100", block_id="BLK-0", interval=TimeInterval(start=t(21, 30), end=t(22, 30)))
        ],
    )
    result = TaskDependencyRule().evaluate(context)
    assert result.status == "FAIL"


def test_unscheduled_predecessor_fails_closed():
    context = ConstraintContext(
        candidate_block=block(),
        tasks=[task("TSK-101", depends_on=["TSK-100"])],
        scheduled_tasks=[],
    )
    result = TaskDependencyRule().evaluate(context)
    assert result.status == "FAIL"
    assert "not scheduled" in result.explanation


def test_predecessor_in_same_block_is_accepted():
    # Both tasks assigned to this candidate — intra-block sequencing deferred
    # to E03 (documented limitation), rule passes.
    context = ConstraintContext(
        candidate_block=block(),
        tasks=[task("TSK-101", depends_on=["TSK-102"]), task("TSK-102")],
    )
    result = TaskDependencyRule().evaluate(context)
    assert result.status == "PASS"


def test_no_dependencies_passes():
    context = ConstraintContext(candidate_block=block(), tasks=[task("TSK-101")])
    result = TaskDependencyRule().evaluate(context)
    assert result.status == "PASS"
