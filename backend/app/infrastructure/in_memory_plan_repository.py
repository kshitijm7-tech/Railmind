from typing import List, Optional
from datetime import datetime, timezone, timedelta
from app.domain.models.planning import Plan, Block, PlanMetrics, PlanVersion, ObjectiveTerm
from app.domain.models.common import TimeInterval, Provenance
from app.domain.enums import PlanStatus, PlanStrategy, DataState, DataSource, BlockStatus

class InMemoryPlanRepository:
    def __init__(self):
        now = datetime.now(timezone.utc)
        self._plans: List[Plan] = [
            Plan(
                plan_id="PLAN-001",
                name="Weekend Track Overhaul",
                horizon=TimeInterval(
                    start=now + timedelta(days=1),
                    end=now + timedelta(days=3)
                ),
                status=PlanStatus.APPROVED,
                strategy=PlanStrategy.BALANCED,
                blocks=[
                    Block(
                        block_id="BLK-1",
                        section_id="SEC-A",
                        interval=TimeInterval(
                            start=now + timedelta(days=1),
                            end=now + timedelta(days=1, hours=8)
                        ),
                        status=BlockStatus.APPROVED,
                        tasks=["TASK-001"],
                        required_power_off=False,
                        is_integrated=True
                    )
                ],
                metrics=PlanMetrics(
                    total_maintenance_time_minutes=480,
                    total_train_delay_minutes=20.5,
                    constraints_violated=0,
                    resource_utilization_percent=85.5,
                    objective_terms=[ObjectiveTerm(name="efficiency", value=10, weight=1.0)],
                    overall_score=95.0
                ),
                version=PlanVersion(
                    version=1,
                    created_at=now.isoformat(),
                    author="planner_bob",
                    changes_summary="Initial version"
                ),
                provenance=Provenance(
                    state=DataState.MOCKED,
                    source=DataSource.SYSTEM,
                    generatedAt=now,
                    generatorVersion="v1.0.0"
                )
            )
        ]

    def get_all(self, page: int, page_size: int) -> tuple[List[Plan], int]:
        start = (page - 1) * page_size
        end = start + page_size
        return self._plans[start:end], len(self._plans)

    def get_by_id(self, plan_id: str) -> Optional[Plan]:
        for p in self._plans:
            if p.plan_id == plan_id:
                return p
        return None

    def save(self, plan: Plan) -> None:
        for idx, p in enumerate(self._plans):
            if p.plan_id == plan.plan_id:
                self._plans[idx] = plan
                return
        self._plans.append(plan)
