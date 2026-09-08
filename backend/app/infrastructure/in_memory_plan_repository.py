from typing import List, Optional
from datetime import datetime, timezone, timedelta
from app.domain.models.planning import Plan, Block, PlanMetrics, PlanVersion
from app.domain.models.common import TimeInterval, Provenance
from app.domain.enums import PlanStatus, PlanStrategy, DataState, DataSource

class InMemoryPlanRepository:
    def __init__(self):
        now = datetime.now(timezone.utc)
        self._plans: List[Plan] = [
            Plan(
                plan_id="PLAN-001",
                name="Weekend Track Overhaul",
                horizon=TimeInterval(
                    startTime=now + timedelta(days=1),
                    endTime=now + timedelta(days=3)
                ),
                status=PlanStatus.APPROVED,
                strategy=PlanStrategy.WEEKEND_CONTINUOUS,
                blocks=[
                    Block(
                        blockId="BLK-1",
                        sectionId="SEC-A",
                        interval=TimeInterval(
                            startTime=now + timedelta(days=1),
                            endTime=now + timedelta(days=1, hours=8)
                        ),
                        taskIds=["TASK-001"]
                    )
                ],
                metrics=PlanMetrics(
                    totalTasksScheduled=1,
                    totalDurationMinutes=480,
                    resourceUtilizationPct=85.5,
                    disruptionScore=2.3
                ),
                version=PlanVersion(
                    versionNumber=1,
                    createdAt=now,
                    createdBy="planner_bob",
                    changes="Initial version"
                ),
                provenance=Provenance(
                    state=DataState.MOCKED,
                    source=DataSource.SYSTEM,
                    generatedAt=now,
                    generatorVersion="v1.0.0"
                )
            ),
            Plan(
                plan_id="PLAN-002",
                name="Nightly Signal Checks",
                horizon=TimeInterval(
                    startTime=now,
                    endTime=now + timedelta(hours=8)
                ),
                status=PlanStatus.DRAFT,
                strategy=PlanStrategy.NIGHT_ONLY,
                blocks=[],
                metrics=PlanMetrics(
                    totalTasksScheduled=2,
                    totalDurationMinutes=180,
                    resourceUtilizationPct=60.0,
                    disruptionScore=1.1
                ),
                version=PlanVersion(
                    versionNumber=1,
                    createdAt=now,
                    createdBy="planner_alice",
                    changes="Drafting signal maintenance plan"
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
