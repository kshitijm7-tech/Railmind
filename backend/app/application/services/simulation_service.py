from typing import List, Optional
import uuid
from datetime import datetime, timezone

from app.domain.models.simulation import SimulationRun, SimulationResult, SimulationStatus
from app.domain.engine.simulation_engine import DeterministicDiscreteEventSimulator
from app.domain.repositories import PlanRepository, OperationsRepository, MaintenanceRepository
from app.api.models import AsyncJob
from app.domain.enums import DataState

class SimulationService:
    def __init__(
        self,
        plan_repo: PlanRepository,
        ops_repo: OperationsRepository,
        maint_repo: MaintenanceRepository
    ):
        self._plan_repo = plan_repo
        self._ops_repo = ops_repo
        self._maint_repo = maint_repo
        self._engine = DeterministicDiscreteEventSimulator()
        
        # In-memory store for simulation runs
        self._runs = {}

    def get_simulation_run(self, run_id: str) -> Optional[SimulationRun]:
        return self._runs.get(run_id)

    def run_simulation(self, plan_id: str, scenario_id: str, data_state: str = DataState.MOCKED.value) -> AsyncJob:
        plan = self._plan_repo.get_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")
            
        train_paths, _ = self._ops_repo.get_all_train_paths(1, 1000)
        tasks, _ = self._maint_repo.get_all_tasks(1, 1000)
        
        now = datetime.now(timezone.utc)
        
        # We execute synchronously for now, returning COMPLETED immediately
        result = self._engine.simulate(
            scenario_id=scenario_id,
            plan=plan,
            train_paths=train_paths,
            tasks=tasks,
            data_state=data_state
        )
        
        sim_run = SimulationRun(
            simulation_run_id=result.simulation_run_id,
            scenario_id=scenario_id,
            plan_id=plan_id,
            plan_version=plan.version.version,
            status=SimulationStatus.COMPLETED,
            engine_version=self._engine.engine_version,
            started_at=now,
            completed_at=datetime.now(timezone.utc),
            configuration={"deterministic_mode": True},
            provenance=result.provenance,
            result=result
        )
        self._runs[sim_run.simulation_run_id] = sim_run
        
        job_id = f"JOB-{uuid.uuid4().hex[:8]}"
        return AsyncJob(
            jobId=job_id,
            status="COMPLETED",
            requestedAt=now.isoformat(),
            startedAt=now.isoformat(),
            completedAt=datetime.now(timezone.utc).isoformat(),
            progressPercent=100,
            resultEndpoint=f"/api/v1/simulations/{sim_run.simulation_run_id}",
            errorCode=None,
            errorMessage=None
        )