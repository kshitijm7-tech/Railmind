import pytest
from datetime import datetime, timedelta
from app.domain.engine.core import ConstraintEngine
from app.domain.engine.rules import (
    OperationalWindowRule,
    MaintenanceDurationRule,
    TrainPathConflictRule,
    PreferredWindowRule
)
from app.domain.engine.models import EvaluationContext, ConstraintSeverity, ConstraintStatus
from app.domain.models.planning import CandidateBlockWindow
from app.domain.models.common import TimeInterval, DurationMinutes
from app.domain.models.maintenance import MaintenanceTask
from app.domain.models.operations import OperationalWindow, TrainPath, PathSegment
from app.domain.enums import TaskType, TaskStatus, Criticality, Department, WindowAvailability

@pytest.fixture
def engine():
    return ConstraintEngine([
        OperationalWindowRule(),
        MaintenanceDurationRule(),
        TrainPathConflictRule(),
        PreferredWindowRule()
    ])

@pytest.fixture
def base_time():
    return datetime(2023, 1, 1, 10, 0, 0) # 10:00 AM

@pytest.fixture
def dummy_task():
    return MaintenanceTask(
        task_id="t1",
        asset_id="a1",
        section_id="s1",
        type=TaskType.INSPECTION,
        status=TaskStatus.SCHEDULED,
        criticality=Criticality.MEDIUM,
        department=Department.TRACK,
        description="Test",
        duration=DurationMinutes(expected=60, minimum=45, maximum=90),
        requires_power_block=False,
        requires_traffic_block=True
    )

def test_operational_window_exact_fit(engine, base_time, dummy_task):
    window = OperationalWindow(
        window_id="w1",
        section_id="s1",
        interval=TimeInterval(start=base_time, end=base_time + timedelta(hours=2)),
        availability=WindowAvailability.AVAILABLE,
        max_trains=0,
        currently_assigned_trains=0
    )
    candidate = CandidateBlockWindow(
        interval=TimeInterval(start=base_time, end=base_time + timedelta(hours=2)),
        suitability_score=100.0,
        conflicts=[]
    )
    context = EvaluationContext(task=dummy_task, windows=[window], paths=[], section_id="s1")
    result = engine.evaluate_candidate(candidate, context)
    
    # Preferred window rule triggers since 10:00 is outside preferred window (22:00-6:00)
    assert result.status == ConstraintStatus.FEASIBLE_WITH_WARNINGS
    assert len(result.violations) == 1
    assert result.violations[0].rule_id == "rule_preferred_window"

def test_operational_window_out_of_bounds(engine, base_time, dummy_task):
    window = OperationalWindow(
        window_id="w1",
        section_id="s1",
        interval=TimeInterval(start=base_time, end=base_time + timedelta(hours=2)),
        availability=WindowAvailability.AVAILABLE,
        max_trains=0,
        currently_assigned_trains=0
    )
    candidate = CandidateBlockWindow(
        interval=TimeInterval(start=base_time - timedelta(minutes=1), end=base_time + timedelta(hours=1)),
        suitability_score=100.0,
        conflicts=[]
    )
    context = EvaluationContext(task=dummy_task, windows=[window], paths=[], section_id="s1")
    result = engine.evaluate_candidate(candidate, context)
    
    assert result.status == ConstraintStatus.INFEASIBLE
    hard_violations = [v for v in result.violations if v.severity == ConstraintSeverity.HARD]
    assert len(hard_violations) == 1
    assert hard_violations[0].rule_id == "rule_operational_window"

def test_maintenance_duration_too_short(engine, base_time, dummy_task):
    window = OperationalWindow(
        window_id="w1",
        section_id="s1",
        interval=TimeInterval(start=base_time, end=base_time + timedelta(hours=2)),
        availability=WindowAvailability.AVAILABLE,
        max_trains=0,
        currently_assigned_trains=0
    )
    # Expected duration is 60m, but candidate is 30m
    candidate = CandidateBlockWindow(
        interval=TimeInterval(start=base_time, end=base_time + timedelta(minutes=30)),
        suitability_score=100.0,
        conflicts=[]
    )
    context = EvaluationContext(task=dummy_task, windows=[window], paths=[], section_id="s1")
    result = engine.evaluate_candidate(candidate, context)
    
    assert result.status == ConstraintStatus.INFEASIBLE
    hard_violations = [v for v in result.violations if v.severity == ConstraintSeverity.HARD]
    assert len(hard_violations) == 1
    assert hard_violations[0].rule_id == "rule_maintenance_duration"

def test_train_path_conflict(engine, base_time, dummy_task):
    window = OperationalWindow(
        window_id="w1",
        section_id="s1",
        interval=TimeInterval(start=base_time, end=base_time + timedelta(hours=2)),
        availability=WindowAvailability.AVAILABLE,
        max_trains=0,
        currently_assigned_trains=0
    )
    candidate = CandidateBlockWindow(
        interval=TimeInterval(start=base_time, end=base_time + timedelta(minutes=60)),
        suitability_score=100.0,
        conflicts=[]
    )
    
    # Train path overlaps (starts 30m after candidate starts, ends 90m after)
    path = TrainPath(
        train_id="tr1",
        segments=[
            PathSegment(
                section_id="s1",
                interval=TimeInterval(start=base_time + timedelta(minutes=30), end=base_time + timedelta(minutes=90)),
                is_conflicted=False
            )
        ],
        constraints=[],
        is_valid=True
    )
    
    context = EvaluationContext(task=dummy_task, windows=[window], paths=[path], section_id="s1")
    result = engine.evaluate_candidate(candidate, context)
    
    assert result.status == ConstraintStatus.INFEASIBLE
    hard_violations = [v for v in result.violations if v.severity == ConstraintSeverity.HARD]
    assert len(hard_violations) == 1
    assert hard_violations[0].rule_id == "rule_train_path_conflict"

def test_train_path_adjacency(engine, base_time, dummy_task):
    # Tests edge cases of overlapping logic
    window = OperationalWindow(
        window_id="w1",
        section_id="s1",
        interval=TimeInterval(start=base_time, end=base_time + timedelta(hours=2)),
        availability=WindowAvailability.AVAILABLE,
        max_trains=0,
        currently_assigned_trains=0
    )
    candidate = CandidateBlockWindow(
        interval=TimeInterval(start=base_time, end=base_time + timedelta(minutes=60)),
        suitability_score=100.0,
        conflicts=[]
    )
    
    # Train starts exactly when candidate ends -> no overlap
    path1 = TrainPath(
        train_id="tr1",
        segments=[
            PathSegment(
                section_id="s1",
                interval=TimeInterval(start=base_time + timedelta(minutes=60), end=base_time + timedelta(minutes=120)),
                is_conflicted=False
            )
        ],
        constraints=[],
        is_valid=True
    )
    
    # Train ends exactly when candidate starts -> no overlap
    path2 = TrainPath(
        train_id="tr2",
        segments=[
            PathSegment(
                section_id="s1",
                interval=TimeInterval(start=base_time - timedelta(minutes=60), end=base_time),
                is_conflicted=False
            )
        ],
        constraints=[],
        is_valid=True
    )
    
    context = EvaluationContext(task=dummy_task, windows=[window], paths=[path1, path2], section_id="s1")
    result = engine.evaluate_candidate(candidate, context)
    
    hard_violations = [v for v in result.violations if v.severity == ConstraintSeverity.HARD]
    assert len(hard_violations) == 0

def test_preferred_window(engine, dummy_task):
    # Candidate starts at 23:00 (Preferred)
    base_time = datetime(2023, 1, 1, 23, 0, 0)
    window = OperationalWindow(
        window_id="w1",
        section_id="s1",
        interval=TimeInterval(start=base_time, end=base_time + timedelta(hours=2)),
        availability=WindowAvailability.AVAILABLE,
        max_trains=0,
        currently_assigned_trains=0
    )
    candidate = CandidateBlockWindow(
        interval=TimeInterval(start=base_time, end=base_time + timedelta(minutes=60)),
        suitability_score=100.0,
        conflicts=[]
    )
    
    context = EvaluationContext(task=dummy_task, windows=[window], paths=[], section_id="s1")
    result = engine.evaluate_candidate(candidate, context)
    
    assert result.status == ConstraintStatus.FEASIBLE
    assert len(result.violations) == 0
