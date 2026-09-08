"""Tests — SOFT rules: preferred window, train impact, workload balance, resource preference.

Soft rules produce PASS/WARNING only and never make a candidate infeasible.
"""

from datetime import timedelta

from engine.constraints.configuration import ConstraintEngineConfig
from engine.constraints.soft.preferred_window import PreferredWindowRule
from engine.constraints.soft.resource_preference import ResourcePreferenceRule
from engine.constraints.soft.train_impact import TrainImpactRule
from engine.constraints.soft.workload_balance import WorkloadBalanceRule
from engine.models.context import ConstraintContext
from engine.models.inputs import (
    CandidateBlock,
    DurationEstimate,
    OperationalWindowRef,
    PathSegmentRef,
    ResourcePool,
    ScheduledTaskRef,
    SectionOccupancy,
    TaskRequirement,
    TimeInterval,
    TrainPathRef,
    WindowAvailability,
)

from engine.tests.helpers import t, t_next


def block(start=None, end=None, section_id="SEC-01") -> CandidateBlock:
    return CandidateBlock(
        section_id=section_id,
        interval=TimeInterval(start=start or t(21), end=end or t(23)),
    )


# ---------------------------------------------------------------------------
# Preferred window (default 22:00–06:00)
# ---------------------------------------------------------------------------


def test_preferred_window_inside_passes():
    # Block 22:30–00:30 lies fully in 22:00–06:00 → PASS
    context = ConstraintContext(candidate_block=block(t(22, 30), t_next(0, 30)))
    result = PreferredWindowRule().evaluate(context)
    assert result.status == "PASS"


def test_preferred_window_outside_warns_not_fails():
    # Day block 14:00–16:00 → WARNING (never FAIL)
    context = ConstraintContext(candidate_block=block(t(14), t(16)))
    result = PreferredWindowRule().evaluate(context)
    assert result.status == "WARNING"
    assert result.constraint_type.value == "SOFT"
    assert result.violation_degree == 120.0


def test_preferred_window_partially_outside_warns_with_exact_minutes():
    # Block 21:00–23:00 → 60 min outside (21:00–22:00)
    context = ConstraintContext(candidate_block=block(t(21), t(23)))
    result = PreferredWindowRule().evaluate(context)
    assert result.status == "WARNING"
    assert result.violation_degree == 60.0


def test_preferred_window_configurable_hours():
    # Reconfigure the preferred window to 20:00–24:00 → 21:00–23:00 passes.
    cfg = ConstraintEngineConfig(preferred_window_start_hour=20, preferred_window_end_hour=0)
    context = ConstraintContext(
        candidate_block=block(t(21), t(23)),
        configuration=cfg,
    )
    result = PreferredWindowRule().evaluate(context)
    assert result.status == "PASS"


# ---------------------------------------------------------------------------
# Train impact (soft proximity)
# ---------------------------------------------------------------------------


def train(train_id, start, end, section_id="SEC-01") -> TrainPathRef:
    return TrainPathRef(
        train_id=train_id,
        segments=[PathSegmentRef(section_id=section_id, interval=TimeInterval(start=start, end=end))],
    )


def test_train_impact_no_trains_passes():
    context = ConstraintContext(candidate_block=block(), train_paths=[])
    result = TrainImpactRule().evaluate(context)
    assert result.status == "PASS"


def test_train_impact_near_miss_warns():
    # Train ends at 20:45; block starts 21:00 → 15 min gap = default buffer boundary
    context = ConstraintContext(
        candidate_block=block(t(21), t(23)),
        train_paths=[train("TRN-1", t(20), t(20, 45))],
    )
    result = TrainImpactRule().evaluate(context)
    assert result.status == "WARNING"
    assert result.constraint_type.value == "SOFT"


def test_train_impact_distant_train_passes():
    # Train ends 18:00 → 180 min gap, beyond default 15 min buffer
    context = ConstraintContext(
        candidate_block=block(t(21), t(23)),
        train_paths=[train("TRN-1", t(16), t(18))],
    )
    result = TrainImpactRule().evaluate(context)
    assert result.status == "PASS"


def test_train_impact_strict_overlap_is_not_this_rule():
    # Overlap is the hard rule's domain; the soft rule ignores it.
    context = ConstraintContext(
        candidate_block=block(t(21), t(23)),
        train_paths=[train("TRN-1", t(21, 30), t(22))],
    )
    result = TrainImpactRule().evaluate(context)
    assert result.status == "PASS"


# ---------------------------------------------------------------------------
# Workload balance
# ---------------------------------------------------------------------------


def task(task_id="TSK-101", expected=60) -> TaskRequirement:
    return TaskRequirement(
        task_id=task_id,
        section_id="SEC-01",
        department="Engineering",
        duration=DurationEstimate(expected=expected, minimum=expected, maximum=expected),
    )


def test_workload_balanced_passes():
    # Candidate load 100 min; other sections 100 min each → 0% deviation
    context = ConstraintContext(
        candidate_block=block(),
        tasks=[task(expected=100)],
        section_occupancies=[
            SectionOccupancy(occupancy_id="O1", section_id="SEC-02",
                             interval=TimeInterval(start=t(21), end=t(22, 40))),
            SectionOccupancy(occupancy_id="O2", section_id="SEC-03",
                             interval=TimeInterval(start=t(21), end=t(22, 40))),
        ],
    )
    result = WorkloadBalanceRule().evaluate(context)
    assert result.status == "PASS"


def test_workload_imbalance_warns_not_fails():
    context = ConstraintContext(
        candidate_block=block(),
        tasks=[task(expected=300)],  # heavy load on SEC-01
        section_occupancies=[
            SectionOccupancy(occupancy_id="O1", section_id="SEC-02",
                             interval=TimeInterval(start=t(21), end=t(23, 30))),
        ],
    )
    result = WorkloadBalanceRule().evaluate(context)
    assert result.status == "WARNING"
    assert result.constraint_type.value == "SOFT"


def test_workload_no_data_passes():
    context = ConstraintContext(candidate_block=block())
    result = WorkloadBalanceRule().evaluate(context)
    assert result.status == "PASS"


# ---------------------------------------------------------------------------
# Resource preference
# ---------------------------------------------------------------------------


def test_resource_preference_all_departments_mapped_passes():
    context = ConstraintContext(
        candidate_block=block(),
        tasks=[task("TSK-101")],
        resource_pools=[ResourcePool(pool_id="P1", department="Engineering", units_available=4)],
    )
    result = ResourcePreferenceRule().evaluate(context)
    assert result.status == "PASS"


def test_resource_preference_unmapped_department_warns():
    context = ConstraintContext(
        candidate_block=block(),
        tasks=[task("TSK-101")],
        resource_pools=[ResourcePool(pool_id="P1", department="S&T", units_available=4)],
    )
    result = ResourcePreferenceRule().evaluate(context)
    assert result.status == "WARNING"


def test_resource_preference_no_tasks_passes():
    context = ConstraintContext(candidate_block=block())
    result = ResourcePreferenceRule().evaluate(context)
    assert result.status == "PASS"
