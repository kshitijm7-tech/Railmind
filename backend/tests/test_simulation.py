import pytest
from datetime import datetime, timezone, timedelta
from app.domain.engine.simulation_engine import DeterministicDiscreteEventSimulator
from app.domain.models.planning import Plan, Block, PlanMetrics, PlanVersion
from app.domain.models.operations import TrainPath, PathSegment
from app.domain.models.maintenance import MaintenanceTask
from app.domain.models.common import TimeInterval, DurationMinutes, Provenance
from app.domain.enums import PlanStatus, PlanStrategy, TaskType, TaskStatus, Criticality, Department

@pytest.fixture
def simulator():
    return DeterministicDiscreteEventSimulator()

def test_simulation_determinism_and_delay(simulator):
    # Setup Data
    start_t = datetime.now(timezone.utc)
    
    # 1. Block covering SEC-1 from start_t to start_t + 120m
    block = Block(
        block_id="BLK-1",
        section_id="SEC-1",
        interval=TimeInterval(start=start_t, end=start_t + timedelta(minutes=120)),
        status="DRAFT",
        tasks=["TASK-1"],
        required_power_off=True,
        is_integrated=False
    )
    
    # 2. Train entering SEC-1 at start_t + 30m, expects to exit at start_t + 60m
    path = TrainPath(
        train_id="TRN-1",
        segments=[
            PathSegment(
                section_id="SEC-1",
                interval=TimeInterval(start=start_t + timedelta(minutes=30), end=start_t + timedelta(minutes=60)),
                is_conflicted=False
            )
        ],
        constraints=[],
        is_valid=True
    )
    
    # 3. Plan
    plan = Plan(
        plan_id="PLAN-1",
        name="Test Plan",
        horizon=TimeInterval(start=start_t, end=start_t + timedelta(hours=4)),
        status=PlanStatus.DRAFT,
        strategy=PlanStrategy.BALANCED,
        blocks=[block],
        metrics=PlanMetrics(total_maintenance_time_minutes=120, total_train_delay_minutes=0, constraints_violated=0, resource_utilization_percent=100),
        version=PlanVersion(version=1, created_at=start_t.isoformat(), author="Test", changes_summary=""),
        provenance=Provenance(state="MOCKED", source="SYSTEM", generatedAt=start_t, generatorVersion="1")
    )
    
    # 4. Task
    task = MaintenanceTask(
        task_id="TASK-1",
        asset_id="AST-1",
        section_id="SEC-1",
        type=TaskType.CORRECTIVE,
        status=TaskStatus.PENDING,
        criticality=Criticality.HIGH,
        department=Department.TRACK,
        description="Fix track",
        duration=DurationMinutes(expected=120, minimum=120, maximum=120),
        requires_power_block=True,
        requires_traffic_block=True
    )
    
    # Simulate A
    res_a = simulator.simulate("SCENARIO-1", plan, [path], [task])
    
    # Assert Delay
    # Train enters at +30m. Block is active until +120m.
    # So train waits from +30m to +120m = 90 mins delay.
    assert res_a.total_delay_minutes == 90.0
    assert res_a.blocked_trains == 1
    assert res_a.completed_maintenance_tasks == 1
    assert "SEC-1" in res_a.affected_sections
    
    # Ensure train blocked event exists
    events = [e.event_type for e in res_a.events]
    assert "TRAIN_BLOCKED" in events
    
    # Simulate B
    res_b = simulator.simulate("SCENARIO-1", plan, [path], [task])
    
    # Assert Determinism
    assert res_a.total_delay_minutes == res_b.total_delay_minutes
    assert res_a.blocked_trains == res_b.blocked_trains
    assert res_a.completed_maintenance_tasks == res_b.completed_maintenance_tasks
    assert len(res_a.events) == len(res_b.events)
    for ea, eb in zip(res_a.events, res_b.events):
        assert ea.event_type == eb.event_type
        assert ea.entity_id == eb.entity_id
