"""Hand-checkable canonical fixtures for E01 (TRD §62: tiny, human-verifiable).

Scenario shape follows the TRD recommendation — 2 tasks, 2 windows, 1
deliberate conflict — plus the reference data each rule needs. Every expected
result is documented inline so a human can verify the fixture without reading
implementation code.

Timeline (all times on 2026-09-14, UTC — a fixed date, never "now"):

    20:00        22:00        00:00        02:00        04:00
     |------------|------------|------------|------------|
     [ NIGHT WINDOW A  (SEC-01, AVAILABLE) ]        ← 20:00–02:00
                  [ NIGHT WINDOW B  (SEC-02, AVAILABLE) ]
                  ^ 22:00–04:00
     [ CONFLICTING TRAIN 10 on SEC-01: 20:00–20:30 ]

    CANDIDATE BLOCK: SEC-01, 22:00–00:00 (120 min) — inside the preferred
    night maintenance window (22:00–06:00) and inside NIGHT WINDOW A.
    Assigned tasks:  TSK-101 (SEC-01, Engineering, 60 min, no deadline)
                     TSK-102 (SEC-01, S&T, 45 min, deadline 2026-09-15 02:00)
    Deliberate conflict: the candidate overlaps NIGHT WINDOW A (fine) but the
    fixture also ships an occupancy on SEC-01 at 22:30–23:30 so tests can
    toggle failures deterministically.

Expected verdicts for the BASE context (all reference data consistent):
    ALL RULES PASS → feasible = True
Expected for the CONFLICT context (occupancy 22:30–23:30 on SEC-01 added):
    RAILMIND.HARD.SECTION_EXCLUSIVITY FAILS → feasible = False
    All other rules unchanged.
"""

from datetime import datetime, timezone

from engine.models.context import ConstraintContext
from engine.models.inputs import (
    CandidateBlock,
    CorridorState,
    DurationEstimate,
    OperationalWindowRef,
    PathSegmentRef,
    ResourcePool,
    ScheduledTaskRef,
    SectionOccupancy,
    SectionState,
    TaskRequirement,
    TimeInterval,
    TrainPathRef,
    WindowAvailability,
)
from engine.models.inputs import SectionStatus


def _t(hour: int, minute: int = 0) -> datetime:
    """Fixed wall-clock time on 2026-09-14, timezone-aware (UTC)."""
    return datetime(2026, 9, 14, hour, minute, tzinfo=timezone.utc)


def _t_next(hour: int, minute: int = 0) -> datetime:
    """Fixed wall-clock time on the following day (2026-09-15), UTC."""
    return datetime(2026, 9, 15, hour, minute, tzinfo=timezone.utc)


DAY = datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc)

# ---------------------------------------------------------------------------
# Canonical identifiers (engine-level mirrors of the canonical dataset ids)
# ---------------------------------------------------------------------------
SECTION_A = "SEC-01"
SECTION_B = "SEC-02"
CORRIDOR = "CORR-07"
TRAIN_10 = "TRN-010"
TASK_101 = "TSK-101"
TASK_102 = "TSK-102"

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------

# 2 windows (TRD style): one per section.
NIGHT_WINDOW_A = OperationalWindowRef(
    window_id="WIN-A",
    section_id=SECTION_A,
    interval=TimeInterval(start=_t(20), end=_t_next(2)),  # 20:00 → 02:00 next day
    availability=WindowAvailability.AVAILABLE,
)
NIGHT_WINDOW_B = OperationalWindowRef(
    window_id="WIN-B",
    section_id=SECTION_B,
    interval=TimeInterval(start=_t(22), end=_t_next(4)),  # 22:00 → 04:00 next day
    availability=WindowAvailability.AVAILABLE,
)

# 1 scheduled train on SEC-01 well clear of the candidate (20:00–20:30 vs 21:00 block).
TRAIN_10_PATH = TrainPathRef(
    train_id=TRAIN_10,
    segments=[
        PathSegmentRef(
            section_id=SECTION_A,
            interval=TimeInterval(start=_t(20), end=_t(20, 30)),
        )
    ],
)

# 2 tasks (TRD style) — durations 60 and 45 minutes.
TASK_101_REQ = TaskRequirement(
    task_id=TASK_101,
    section_id=SECTION_A,
    department="Engineering",
    duration=DurationEstimate(expected=60, minimum=45, maximum=90),
    crew_units_required=4,
    latest_finish=None,
    depends_on=[],
)
TASK_102_REQ = TaskRequirement(
    task_id=TASK_102,
    section_id=SECTION_A,  # bundled into the SEC-01 block for the base scenario
    department="S&T",
    duration=DurationEstimate(expected=45, minimum=30, maximum=60),
    crew_units_required=2,
    latest_finish=_t_next(2),  # 02:00 next day — block ends 23:00, slack 180 min
    depends_on=[],
)

RESOURCE_POOLS = [
    ResourcePool(pool_id="POOL-ENG", department="Engineering", units_available=8),
    ResourcePool(pool_id="POOL-ST", department="S&T", units_available=6),
]

SECTION_STATES = [
    SectionState(section_id=SECTION_A, status=SectionStatus.OPEN),
    SectionState(section_id=SECTION_B, status=SectionStatus.OPEN),
]

CORRIDORS = [
    CorridorState(corridor_id=CORRIDOR, section_ids=[SECTION_A, SECTION_B], is_available=True)
]

PLANNING_HORIZON = TimeInterval(start=DAY, end=datetime(2026, 9, 17, 0, 0, tzinfo=timezone.utc))


# ---------------------------------------------------------------------------
# Candidate block (21:00–23:00 on SEC-01, 120 min, carries both tasks)
# ---------------------------------------------------------------------------
def base_candidate() -> CandidateBlock:
    return CandidateBlock(
        block_id="BLK-CAND",
        section_id=SECTION_A,
        interval=TimeInterval(start=_t(22), end=_t_next(0)),
        task_ids=[TASK_101, TASK_102],
        resource_pool_ids=[],
    )


def base_context() -> ConstraintContext:
    """The BASE fixture: every documented rule passes → feasible."""
    return ConstraintContext(
        candidate_block=base_candidate(),
        tasks=[TASK_101_REQ, TASK_102_REQ],
        train_paths=[TRAIN_10_PATH],
        operational_windows=[NIGHT_WINDOW_A, NIGHT_WINDOW_B],
        section_occupancies=[],
        section_states=SECTION_STATES,
        corridors=CORRIDORS,
        resource_pools=RESOURCE_POOLS,
        resource_demands=[],
        planning_horizon=PLANNING_HORIZON,
    )


def conflict_context() -> ConstraintContext:
    """BASE + one deliberate 22:30–23:30 occupancy on SEC-01.

    Expected: RAILMIND.HARD.SECTION_EXCLUSIVITY FAILS (60 min overlap with the
    candidate's 22:00–00:00 interval); every other result unchanged; the
    evaluation becomes infeasible.
    """
    occupancy = SectionOccupancy(
        occupancy_id="OCC-900",
        section_id=SECTION_A,
        interval=TimeInterval(start=_t(22, 30), end=_t(23, 30)),
        kind="MAINTENANCE",
    )  # overlaps the 22:00–00:00 candidate by 60 minutes
    return base_context().model_copy(
        update={"section_occupancies": [occupancy]},
    )


__all__ = [
    "SECTION_A",
    "SECTION_B",
    "CORRIDOR",
    "TRAIN_10",
    "TASK_101",
    "TASK_102",
    "base_candidate",
    "base_context",
    "conflict_context",
]
