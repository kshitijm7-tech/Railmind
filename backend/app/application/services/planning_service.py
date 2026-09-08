import uuid
from datetime import datetime, timezone
from typing import List, Tuple, Dict, Any

from app.domain.repositories import (
    PlanRepository,
    InfrastructureRepository,
    MaintenanceRepository,
    OperationsRepository
)
from app.domain.models.planning import Plan, Block, PlanMetrics, PlanVersion
from app.domain.models.common import TimeInterval, Provenance
from app.domain.enums import PlanStatus, PlanStrategy, DataState, DataSource, BlockStatus
from app.domain.logic.planning import CandidateGenerator, ConflictDetector
from app.api.models import GeneratePlanRequest, AsyncJob, ComparePlansResponse, PlanComparisonEntry

class PlanningService:
    def __init__(
        self,
        plan_repo: PlanRepository,
        infra_repo: InfrastructureRepository,
        maint_repo: MaintenanceRepository,
        ops_repo: OperationsRepository
    ):
        self._plan_repo = plan_repo
        self._infra_repo = infra_repo
        self._maint_repo = maint_repo
        self._ops_repo = ops_repo
        self._generator = CandidateGenerator()
        self._detector = ConflictDetector()

    def get_plans(self, page: int, page_size: int) -> Tuple[List[Plan], int]:
        return self._plan_repo.get_all(page, page_size)

    def get_plan(self, plan_id: str) -> Plan | None:
        return self._plan_repo.get_by_id(plan_id)

    def generate_plan(self, request: GeneratePlanRequest) -> AsyncJob:
        # Step 1: Fetch tasks
        tasks, _ = self._maint_repo.get_all_tasks(1, 1000)
        if request.taskIds:
            tasks = [t for t in tasks if t.task_id in request.taskIds]

        # Step 2: Fetch ops context
        windows, _ = self._ops_repo.get_all_operational_windows(1, 1000)
        paths, _ = self._ops_repo.get_all_train_paths(1, 1000)

        # Step 3: Generate blocks deterministically
        blocks = []
        for t in tasks:
            candidates = self._generator.generate_candidates(t, windows)
            # Evaluate conflicts
            evaluated = []
            for c in candidates:
                c_eval = self._detector.detect_conflicts(c, paths, t.section_id)
                evaluated.append(c_eval)
            
            # Select first candidate with 0 conflicts, else the one with least
            if evaluated:
                evaluated.sort(key=lambda x: len(x.conflicts))
                chosen = evaluated[0]
                blocks.append(Block(
                    block_id=f"BLK-{uuid.uuid4().hex[:6]}",
                    section_id=t.section_id,
                    interval=chosen.interval,
                    status=BlockStatus.DRAFT,
                    tasks=[t.task_id],
                    required_power_off=t.requires_power_block,
                    is_integrated=False
                ))

        # Step 4: Construct Plan
        now = datetime.now(timezone.utc)
        plan_id = f"PLAN-{uuid.uuid4().hex[:6]}"
        plan = Plan(
            plan_id=plan_id,
            name=f"Generated Plan - {request.corridorId}",
            horizon=request.horizon,
            status=PlanStatus.DRAFT,
            strategy=request.strategy,
            blocks=blocks,
            metrics=PlanMetrics(
                total_maintenance_time_minutes=sum(t.duration.expected for t in tasks),
                total_train_delay_minutes=0.0,
                constraints_violated=sum(1 for b in blocks if len(b.tasks) == 0),
                resource_utilization_percent=75.0,
                objective_terms=[],
                overall_score=80.0
            ),
            version=PlanVersion(
                version=1,
                created_at=now.isoformat(),
                author="System",
                changes_summary="Auto-generated plan"
            ),
            provenance=Provenance(
                state=DataState.MOCKED,
                source=DataSource.SYSTEM,
                generatedAt=now,
                generatorVersion="v1.0.0"
            )
        )
        self._plan_repo.save(plan)

        # Step 5: Return AsyncJob
        job_id = f"JOB-{uuid.uuid4().hex[:8]}"
        return AsyncJob(
            jobId=job_id,
            status="COMPLETED",
            requestedAt=now.isoformat(),
            startedAt=now.isoformat(),
            completedAt=now.isoformat(),
            progressPercent=100,
            resultEndpoint=f"/api/v1/plans/{plan_id}",
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
