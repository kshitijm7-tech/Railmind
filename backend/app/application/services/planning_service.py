import uuid
from datetime import datetime, timezone
from typing import List, Tuple, Dict, Any

from app.domain.repositories import (
    PlanRepository,
    InfrastructureRepository,
    MaintenanceRepository,
    OperationsRepository
)
from app.domain.models.planning import Plan, Block, PlanMetrics, PlanVersion, ObjectiveTerm
from app.domain.models.common import TimeInterval, Provenance
from app.domain.enums import PlanStatus, PlanStrategy, DataState, DataSource, BlockStatus
from app.domain.logic.planning import CandidateGenerator, ConflictDetector
from app.api.models import GeneratePlanRequest, AsyncJob, ComparePlansResponse, PlanComparisonEntry
from app.domain.engine.optimization_engine import DeterministicBaselineOptimizer
from app.application.services.priority_service import PriorityService

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
        self._priority_service = PriorityService()
        self._optimizer = DeterministicBaselineOptimizer()

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

        # Step 3: Evaluate Priorities (P10)
        defects, _ = self._maint_repo.get_all_defects(1, 1000)
        defects_by_task = {d.linked_task_id: d for d in defects if d.linked_task_id}
        
        # Simplified: no pre-calculated impacts for priority right now
        impacts_by_task = {}
        
        priority_results_list = self._priority_service.evaluate_tasks(
            tasks=tasks,
            defects_by_task=defects_by_task,
            impacts_by_task=impacts_by_task
        )
        priorities = {r.task_id: r for r in priority_results_list}

        # Step 4: Generate & Evaluate Candidates (P07 + P09)
        candidates_by_task = {}
        for t in tasks:
            raw_candidates = self._generator.generate_candidates(t, windows)
            evaluated = []
            for c in raw_candidates:
                c_eval = self._detector.detect_conflicts(c, paths, t.section_id, t, windows)
                evaluated.append(c_eval)
            candidates_by_task[t.task_id] = evaluated

        # Step 5: Optimize (P11)
        plan_id = f"PLAN-{uuid.uuid4().hex[:6].upper()}"
        opt_result = self._optimizer.optimize(
            tasks=tasks,
            windows=windows,
            paths=paths,
            priorities=priorities,
            candidates_by_task=candidates_by_task,
            plan_id=plan_id
        )

        blocks = opt_result.selected_blocks
        bd = opt_result.objective_breakdown

        # Convert breakdown to PlanMetrics objective_terms
        objective_terms = [
            ObjectiveTerm(name="Priority Value", value=bd.priority_value, weight=self._optimizer.config.priority_weight),
            ObjectiveTerm(name="Tasks Completed", value=bd.tasks_completed, weight=self._optimizer.config.task_completion_weight),
            ObjectiveTerm(name="Window Utilization", value=bd.window_utilization, weight=self._optimizer.config.window_utilization_weight),
            ObjectiveTerm(name="Train Impact Cost", value=-bd.train_impact_cost, weight=self._optimizer.config.train_impact_penalty),
            ObjectiveTerm(name="Operational Impact", value=-bd.operational_impact_cost, weight=self._optimizer.config.operational_impact_penalty),
        ]

        # Step 6: Construct Plan
        now = datetime.now(timezone.utc)
        plan = Plan(
            plan_id=plan_id,
            name=f"Optimized Plan - {request.corridorId or 'ALL'}",
            horizon=request.horizon,
            status=PlanStatus.DRAFT,
            strategy=request.strategy,
            blocks=blocks,
            metrics=PlanMetrics(
                total_maintenance_time_minutes=sum(t.duration.expected for t in tasks if t.task_id not in opt_result.unselected_tasks),
                total_train_delay_minutes=bd.train_impact_cost, # Simplification
                constraints_violated=0, # Optimizer filters hard violations
                resource_utilization_percent=bd.window_utilization,
                objective_terms=objective_terms,
                overall_score=opt_result.objective_score
            ),
            version=PlanVersion(
                version=1,
                created_at=now.isoformat(),
                author=opt_result.solver_name,
                changes_summary=f"Optimized {len(blocks)} blocks. Unselected {len(opt_result.unselected_tasks)} tasks."
            ),
            provenance=Provenance(
                state=DataState.MOCKED,
                source=DataSource.SYSTEM,
                generatedAt=now,
                generatorVersion=opt_result.solver_version
            )
        )
        self._plan_repo.save(plan)

        # Step 7: Return AsyncJob
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