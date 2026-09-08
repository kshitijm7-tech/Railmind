"""Tests — HARD rule: resource exclusivity and crew capacity."""

from engine.constraints.hard.resource_exclusivity import ResourceExclusivityRule
from engine.models.context import ConstraintContext
from engine.models.inputs import (
    CandidateBlock,
    DurationEstimate,
    ResourceDemand,
    ResourcePool,
    TaskRequirement,
    TimeInterval,
)

from engine.tests.helpers import t, t_next


def block() -> CandidateBlock:
    return CandidateBlock(section_id="SEC-01", interval=TimeInterval(start=t(21), end=t(23)))


def task(department="Engineering", crew=4, task_id="TSK-101") -> TaskRequirement:
    return TaskRequirement(
        task_id=task_id,
        section_id="SEC-01",
        department=department,
        duration=DurationEstimate(expected=60, minimum=45, maximum=90),
        crew_units_required=crew,
    )


def pool(department="Engineering", units=8, pool_id="POOL-1", exclusive=False) -> ResourcePool:
    return ResourcePool(pool_id=pool_id, department=department, units_available=units, is_exclusive=exclusive)


def demand(demand_id, pool_id, units, start=None, end=None) -> ResourceDemand:
    return ResourceDemand(
        demand_id=demand_id,
        pool_id=pool_id,
        units=units,
        interval=TimeInterval(start=start or t(21), end=end or t(22)),
    )


def evaluate(block_obj, tasks, pools, demands) -> object:
    context = ConstraintContext(
        candidate_block=block_obj, tasks=tasks, resource_pools=pools, resource_demands=demands
    )
    return ResourceExclusivityRule().evaluate(context)


def test_capacity_within_limit_passes():
    result = evaluate(block(), [task(crew=4)], [pool(units=8)], [])
    assert result.status == "PASS"


def test_capacity_exceeded_fails_with_deficit():
    # Needs 4 + committed 5 = 9 > 8 → FAIL, deficit 1
    result = evaluate(block(), [task(crew=4)], [pool(units=8)], [demand("D-1", "POOL-1", 5)])
    assert result.status == "FAIL"
    assert result.violation_degree == 1.0


def test_pool_not_covering_block_interval_fails():
    # Pool shift ends before the block starts → cannot staff
    early_pool = ResourcePool(
        pool_id="POOL-EARLY", department="Engineering", units_available=8,
        availability=TimeInterval(start=t(6), end=t(20)),
    )
    result = evaluate(block(), [task(crew=4)], [early_pool], [])
    assert result.status == "FAIL"
    assert "does not cover" in result.explanation


def test_department_without_pool_fails_closed():
    result = evaluate(block(), [task(department="TRD")], [pool(department="Engineering")], [])
    assert result.status == "FAIL"
    assert "fail-closed" in result.explanation


def test_zero_crew_task_does_not_demand_pool():
    # crew_units_required = 0 → no staffing constraint
    result = evaluate(block(), [task(crew=0)], [], [])
    assert result.status == "PASS"


def test_exclusive_pool_double_booked_fails():
    result = evaluate(
        block(),
        [],
        [pool(pool_id="POOL-X", exclusive=True)],
        [demand("D-9", "POOL-X", 1)],
    )
    # Block does not claim the pool explicitly; existing demand alone is fine.
    assert result.status == "PASS"

    claiming_block = CandidateBlock(
        section_id="SEC-01",
        interval=TimeInterval(start=t(21), end=t(23)),
        resource_pool_ids=["POOL-X"],
    )
    result = evaluate(claiming_block, [], [pool(pool_id="POOL-X", exclusive=True)], [demand("D-9", "POOL-X", 1)])
    assert result.status == "FAIL"
    assert "double-booked" in result.message.lower()


def test_exclusive_pool_claimed_without_clash_passes():
    claiming_block = CandidateBlock(
        section_id="SEC-01",
        interval=TimeInterval(start=t(21), end=t(23)),
        resource_pool_ids=["POOL-X"],
    )
    result = evaluate(claiming_block, [], [pool(pool_id="POOL-X", exclusive=True)], [])
    assert result.status == "PASS"


def test_adjacent_demand_does_not_consume_capacity():
    # Existing demand 20:00–21:00 is adjacent to block start → not counted
    result = evaluate(
        block(),
        [task(crew=4)],
        [pool(units=4)],
        [demand("D-1", "POOL-1", 4, start=t(20), end=t(21))],
    )
    assert result.status == "PASS"


def test_multiple_pools_all_checked():
    result = evaluate(
        block(),
        [task("Engineering", 4, "TSK-101"), task("S&T", 3, "TSK-102")],
        [pool("Engineering", 4, "POOL-1"), pool("S&T", 2, "POOL-2")],
        [],
    )
    assert result.status == "FAIL"  # S&T needs 3 > 2
    assert any("POOL-2" in e.source for e in result.evidence)
