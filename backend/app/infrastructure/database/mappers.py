from app.infrastructure.database.models import (
    PlanORM, BlockORM, MaintenanceTaskORM, CorridorORM, TrackSectionORM, AssetORM, TrainORM, TrainPathORM, SimulationRunORM, DecisionORM
)
from app.domain.models.planning import Plan, Block, PlanMetrics, PlanVersion
from app.domain.models.maintenance import MaintenanceTask, Defect
from app.domain.models.operations import Train, TrainService, TrainPath, PathSegment, SectionTiming
from app.domain.models.infrastructure import Corridor, TrackSection, RailwayAsset
from app.domain.models.decision import Decision
from app.domain.models.simulation import SimulationRun, SimulationResult, SimulationEvent
from app.domain.models.common import TimeInterval, DurationMinutes, Provenance

# Implement mappers here if we actually use them, but let's keep it simple.

def to_plan_domain(orm: PlanORM) -> Plan:
    return Plan(
        plan_id=orm.plan_id,
        name=orm.name,
        horizon=TimeInterval(start=orm.start_time, end=orm.end_time),
        status=orm.status,
        strategy=orm.strategy,
        blocks=[
            Block(
                block_id=b.block_id,
                section_id=b.section_id,
                interval=TimeInterval(start=b.start_time, end=b.end_time),
                status=b.status,
                required_power_off=b.required_power_off,
                is_integrated=b.is_integrated,
                tasks=b.tasks
            )
            for b in orm.blocks
        ],
        metrics=PlanMetrics(**orm.metrics),
        version=PlanVersion(**orm.version),
        provenance=Provenance(**orm.provenance)
    )

def to_plan_orm(domain: Plan) -> PlanORM:
    blocks = [
        BlockORM(
            block_id=b.block_id,
            plan_id=domain.plan_id,
            section_id=b.section_id,
            start_time=b.interval.start,
            end_time=b.interval.end,
            status=b.status,
            required_power_off=b.required_power_off,
            is_integrated=b.is_integrated,
            tasks=b.tasks
        )
        for b in domain.blocks
    ]
    
    return PlanORM(
        plan_id=domain.plan_id,
        name=domain.name,
        start_time=domain.horizon.start,
        end_time=domain.horizon.end,
        status=domain.status.value if hasattr(domain.status, 'value') else domain.status,
        strategy=domain.strategy.value if hasattr(domain.strategy, 'value') else domain.strategy,
        metrics=domain.metrics.model_dump(mode="json"),
        version=domain.version.model_dump(mode="json"),
        provenance=domain.provenance.model_dump(mode="json"),
        blocks=blocks
    )