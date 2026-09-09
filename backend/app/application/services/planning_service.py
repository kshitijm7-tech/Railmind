import uuid
from datetime import datetime, timezone
from typing import List, Tuple, Dict, Any, Optional

from app.domain.repositories import (
    PlanRepository,
    InfrastructureRepository,
    MaintenanceRepository,
    OperationsRepository
)
from app.domain.models.planning import Plan, Block, PlanMetrics, PlanVersion, ObjectiveTerm
from app.domain.models.common import TimeInterval, Provenance
from app.domain.enums import PlanStatus, PlanStrategy, DataState, DataSource, BlockStatus
from app.api.models import GeneratePlanRequest, AsyncJob, ComparePlansResponse, PlanComparisonEntry
from app.api.schemas.engine import (
    PrioritizeTaskRequest,
    PlanGenerationRequest,
    PlanTask,
    PlanWindow,
    PlanCrewPool,
    WindowDelayRequest,
    AffectedTrainRequest
)
from app.engine_adapter.service import EngineIntegrationService

class PlanningService:
    def __init__(
        self,
        plan_repo: PlanRepository,
        infra_repo: InfrastructureRepository,
        maint_repo: MaintenanceRepository,
        ops_repo: OperationsRepository,
        engine_service: EngineIntegrationService
    ):
        self._plan_repo = plan_repo
        self._infra_repo = infra_repo
        self._maint_repo = maint_repo
        self._ops_repo = ops_repo
        self._engine_service = engine_service

    def get_plans(self, page: int, page_size: int) -> Tuple[List[Plan], int]:
        return self._plan_repo.get_all(page, page_size)

    def get_plan(self, plan_id: str) -> Plan | None:
        return self._plan_repo.get_by_id(plan_id)

    def generate_plan(self, request: GeneratePlanRequest) -> AsyncJob:
        # Step 1: Fetch data
        tasks, _ = self._maint_repo.get_all_tasks(1, 1000)
        if request.taskIds:
            tasks = [t for t in tasks if t.task_id in request.taskIds]

        windows, _ = self._ops_repo.get_all_operational_windows(1, 1000)
        
        # Step 2: Use E02 to prioritize tasks
        plan_tasks = []
        for t in tasks:
            req = PrioritizeTaskRequest(
                taskId=t.task_id,
                sectionId=t.section_id,
                criticality=t.criticality.value if hasattr(t.criticality, "value") else str(t.criticality),
                overdueDays=5, # Simplified
                taskType="CORRECTIVE", # Simplified for integration
            )
            e02_resp = self._engine_service.prioritize(req)
            
            pt = PlanTask(
                taskId=t.task_id,
                durationMinutes=t.duration.expected,
                department=t.department.value if hasattr(t.department, "value") else str(t.department),
                crewSize=1,
                priority=e02_resp,
                latestFinish=None,
                precedes=[]
            )
            plan_tasks.append(pt)

        # Step 3: Map windows
        plan_windows = []
        for w in windows:
            pw = PlanWindow(
                windowId=w.window_id,
                sectionId=w.section_id,
                earliestStart=w.interval.start,
                latestEnd=w.interval.end,
                maxDurationMinutes=(w.interval.end - w.interval.start).total_seconds() / 60.0,
                qualifiedDepartments=[],
                bundleBonus=0.0,
                overrunRisk=0.0
            )
            plan_windows.append(pw)

        # Step 4: Run E09 Engine
        plan_ref = f"PLAN-{uuid.uuid4().hex[:6].upper()}"
        engine_req = PlanGenerationRequest(
            planRef=plan_ref,
            tasks=plan_tasks,
            windows=plan_windows,
            crewPools=[],
            delayInputs={},
            alternativeCount=0
        )
        engine_resp = self._engine_service.generate_plan(engine_req)

        # Step 5: Process generated plan
        best_plan = engine_resp.plans[0] if engine_resp.plans else None
        
        blocks = []
        unselected_tasks = []
        if best_plan:
            for b in best_plan.blocks:
                block = Block(
                    block_id=f"BLK-{uuid.uuid4().hex[:6].upper()}",
                    section_id=next((w.sectionId for w in plan_windows if w.windowId == b.windowId), "SEC-UNK"),
                    interval=TimeInterval(
                        start=next((w.earliestStart for w in plan_windows if w.windowId == b.windowId), now),
                        end=next((w.latestEnd for w in plan_windows if w.windowId == b.windowId), now)
                    ),
                    status=BlockStatus.SCHEDULED,
                    tasks=b.taskIds,
                    required_power_off=False,
                    is_integrated=False
                )
                blocks.append(block)
            unselected_tasks = best_plan.unscheduledTaskIds
        
        now = datetime.now(timezone.utc)
        
        # Extract metadata properly
        total_time = sum(t.duration.expected for t in tasks if t.task_id not in unselected_tasks)
        overall_score = best_plan.objective.totalObjective if best_plan else 0.0
        
        plan = Plan(
            plan_id=plan_ref,
            name=f"E09 Optimized Plan - {request.corridorId or 'ALL'}",
            horizon=request.horizon,
            status=PlanStatus.DRAFT,
            strategy=request.strategy,
            blocks=blocks,
            metrics=PlanMetrics(
                total_maintenance_time_minutes=total_time,
                total_train_delay_minutes=0.0,
                constraints_violated=0,
                resource_utilization_percent=0.8,
                objective_terms=[],
                overall_score=overall_score
            ),
            version=PlanVersion(
                version=1,
                created_at=now.isoformat(),
                author=engine_resp.evidence.solverVersion,
                changes_summary=f"E09 generated. {len(blocks)} blocks. Unscheduled: {len(unselected_tasks)}"
            ),
            provenance=Provenance(
                state=DataState.MOCKED,
                source=DataSource.SYSTEM,
                generatedAt=now,
                generatorVersion=engine_resp.evidence.solverVersion
            )
        )
        self._plan_repo.save(plan)

        # Step 6: Return AsyncJob
        job_id = f"JOB-{uuid.uuid4().hex[:8]}"
        return AsyncJob(
            jobId=job_id,
            status="COMPLETED",
            requestedAt=now.isoformat(),
            startedAt=now.isoformat(),
            completedAt=now.isoformat(),
            progressPercent=100,
            resultEndpoint=f"/api/v1/plans/{plan_ref}",
            errorCode=None,
            errorMessage=None
        )

    def compare_plans(self, plan_ids: List[str]) -> ComparePlansResponse:
        candidates = []
        for pid in plan_ids:
            plan = self._plan_repo.get_by_id(pid)
            if plan:
                candidates.append(PlanComparisonEntry(
                    planId=plan.plan_id,
                    planName=plan.name,
                    strategy=plan.strategy,
                    metrics=plan.metrics,
                    trainImpactCount=0,
                    constraintViolations=plan.metrics.constraints_violated,
                    overrunRisk=0.1,
                    recommendationRank=1
                ))
        
        candidates.sort(key=lambda x: x.metrics.overall_score or 0, reverse=True)
        for idx, c in enumerate(candidates):
            c.recommendationRank = idx + 1
            
        recommended = candidates[0].planId if candidates else ""

        return ComparePlansResponse(
            candidates=candidates,
            recommendedPlanId=recommended,
            tradeoffSummary=["Plan 1 minimizes delay", "Plan 2 maximizes maintenance"]
        )