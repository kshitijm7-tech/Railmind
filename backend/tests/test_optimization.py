"""
P11 Block Optimization Engine Tests
===================================
Tests cover:
  - Deterministic evaluation
  - Hard constraint handling
  - Priority vs Utilisation 
  - Tie-breaking
"""
import pytest
from datetime import datetime, timezone, timedelta
from app.domain.engine.optimization_engine import DeterministicBaselineOptimizer, OptimizationConfiguration
from app.domain.engine.priority_models import PriorityResult, PriorityClass, PriorityFactorResult
from app.domain.models.maintenance import MaintenanceTask
from app.domain.models.operations import OperationalWindow, TrainPath
from app.domain.models.planning import CandidateBlockWindow
from app.domain.models.common import TimeInterval, DurationMinutes
from app.domain.enums import Criticality, TaskType, TaskStatus, Department, WindowAvailability

@pytest.fixture
def optimizer():
    return DeterministicBaselineOptimizer()

def test_optimization_selects_feasible_task(optimizer):
    task = MaintenanceTask(
        task_id="TASK-OPT-1",
        asset_id="AST-1",
        section_id="SEC-1",
        type=TaskType.CORRECTIVE,
        status=TaskStatus.PENDING,
        criticality=Criticality.HIGH,
        department=Department.TRACK,
        description="Test",
        duration=DurationMinutes(expected=60, minimum=60, maximum=60),
        requires_power_block=False,
        requires_traffic_block=False
    )
    
    t_start = datetime.now(timezone.utc)
    cand = CandidateBlockWindow(
        interval=TimeInterval(start=t_start, end=t_start + timedelta(minutes=60)),
        suitability_score=100.0,
        violations=[],
        conflicts=[]
    )
    
    priority = PriorityResult(
        task_id="TASK-OPT-1",
        score=90.0,
        priority_class=PriorityClass.CRITICAL,
        factors=[],
        explanation="",
        engine_version="",
        calculated_at=t_start,
        data_state="MOCKED"
    )
    
    result = optimizer.optimize(
        tasks=[task],
        windows=[],
        paths=[],
        priorities={"TASK-OPT-1": priority},
        candidates_by_task={"TASK-OPT-1": [cand]}
    )
    
    assert len(result.selected_blocks) == 1
    assert result.selected_blocks[0].tasks == ["TASK-OPT-1"]
    assert result.objective_breakdown.priority_value == 90.0
    assert result.objective_score > 90.0

def test_optimization_rejects_hard_constraint(optimizer):
    task = MaintenanceTask(
        task_id="TASK-OPT-2",
        asset_id="AST-1",
        section_id="SEC-1",
        type=TaskType.CORRECTIVE,
        status=TaskStatus.PENDING,
        criticality=Criticality.HIGH,
        department=Department.TRACK,
        description="Test",
        duration=DurationMinutes(expected=60, minimum=60, maximum=60),
        requires_power_block=False,
        requires_traffic_block=False
    )
    
    t_start = datetime.now(timezone.utc)
    cand = CandidateBlockWindow(
        interval=TimeInterval(start=t_start, end=t_start + timedelta(minutes=60)),
        suitability_score=100.0,
        violations=[{"severity": "HARD", "message": "Conflict"}],
        conflicts=["Conflict"]
    )
    
    priority = PriorityResult(
        task_id="TASK-OPT-2",
        score=90.0,
        priority_class=PriorityClass.CRITICAL,
        factors=[],
        explanation="",
        engine_version="",
        calculated_at=t_start,
        data_state="MOCKED"
    )
    
    result = optimizer.optimize(
        tasks=[task],
        windows=[],
        paths=[],
        priorities={"TASK-OPT-2": priority},
        candidates_by_task={"TASK-OPT-2": [cand]}
    )
    
    assert len(result.selected_blocks) == 0
    assert "TASK-OPT-2" in result.unselected_tasks

def test_optimization_prevents_overlap_same_section(optimizer):
    task1 = MaintenanceTask(
        task_id="TASK-OPT-1",
        asset_id="AST-1",
        section_id="SEC-1",
        type=TaskType.CORRECTIVE,
        status=TaskStatus.PENDING,
        criticality=Criticality.HIGH,
        department=Department.TRACK,
        description="Test1",
        duration=DurationMinutes(expected=60, minimum=60, maximum=60),
        requires_power_block=False,
        requires_traffic_block=False
    )
    task2 = MaintenanceTask(
        task_id="TASK-OPT-2",
        asset_id="AST-2",
        section_id="SEC-1", # Same section
        type=TaskType.CORRECTIVE,
        status=TaskStatus.PENDING,
        criticality=Criticality.MEDIUM,
        department=Department.TRACK,
        description="Test2",
        duration=DurationMinutes(expected=60, minimum=60, maximum=60),
        requires_power_block=False,
        requires_traffic_block=False
    )
    
    t_start = datetime.now(timezone.utc)
    # Both tasks have a candidate exactly at the same time
    cand1 = CandidateBlockWindow(
        interval=TimeInterval(start=t_start, end=t_start + timedelta(minutes=60)),
        suitability_score=100.0,
        violations=[],
        conflicts=[]
    )
    cand2 = CandidateBlockWindow(
        interval=TimeInterval(start=t_start, end=t_start + timedelta(minutes=60)),
        suitability_score=100.0,
        violations=[],
        conflicts=[]
    )
    
    priority1 = PriorityResult(
        task_id="TASK-OPT-1", score=90.0, priority_class=PriorityClass.CRITICAL, factors=[], explanation="", engine_version="", calculated_at=t_start, data_state="MOCKED"
    )
    priority2 = PriorityResult(
        task_id="TASK-OPT-2", score=50.0, priority_class=PriorityClass.MEDIUM, factors=[], explanation="", engine_version="", calculated_at=t_start, data_state="MOCKED"
    )
    
    result = optimizer.optimize(
        tasks=[task1, task2],
        windows=[],
        paths=[],
        priorities={"TASK-OPT-1": priority1, "TASK-OPT-2": priority2},
        candidates_by_task={"TASK-OPT-1": [cand1], "TASK-OPT-2": [cand2]}
    )
    
    assert len(result.selected_blocks) == 1
    assert result.selected_blocks[0].tasks == ["TASK-OPT-1"]
    assert "TASK-OPT-2" in result.unselected_tasks