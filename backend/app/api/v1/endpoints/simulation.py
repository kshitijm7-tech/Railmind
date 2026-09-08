from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid

from app.api.dependencies import get_simulation_service
from app.application.services.simulation_service import SimulationService
from app.api.models import ApiResponse, AsyncJob, ApiMeta
from app.domain.models.simulation import SimulationRun, SimulationEvent, SimulationResult

router = APIRouter()

def create_meta() -> ApiMeta:
    return ApiMeta(
        timestamp=datetime.now(timezone.utc).isoformat(),
        requestId=str(uuid.uuid4()),
        version="v1"
    )


class RunSimulationRequest(BaseModel):
    plan_id: str
    scenario_id: str
    data_state: Optional[str] = "MOCKED"

@router.post("", response_model=AsyncJob, status_code=202)
def run_simulation(
    request: RunSimulationRequest,
    service: SimulationService = Depends(get_simulation_service)
):
    try:
        job = service.run_simulation(
            plan_id=request.plan_id,
            scenario_id=request.scenario_id,
            data_state=request.data_state or "MOCKED"
        )
        return job
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{run_id}", response_model=ApiResponse[SimulationRun])
def get_simulation_run(
    run_id: str,
    service: SimulationService = Depends(get_simulation_service)
):
    run = service.get_simulation_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found")
    
    return ApiResponse(
        success=True,
        meta=create_meta(),
        data=run
    )

@router.get("/{run_id}/events", response_model=ApiResponse[List[SimulationEvent]])
def get_simulation_events(
    run_id: str,
    service: SimulationService = Depends(get_simulation_service)
):
    run = service.get_simulation_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found")
        
    return ApiResponse(
        success=True,
        meta=create_meta(),
        data=run.result.events if run.result else []
    )

@router.get("/{run_id}/results", response_model=ApiResponse[SimulationResult])
def get_simulation_result(
    run_id: str,
    service: SimulationService = Depends(get_simulation_service)
):
    run = service.get_simulation_run(run_id)
    if not run or not run.result:
        raise HTTPException(status_code=404, detail="Simulation result not found")
        
    return ApiResponse(
        success=True,
        meta=create_meta(),
        data=run.result
    )