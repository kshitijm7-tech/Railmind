from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from app.api.models import ApiResponse, ApiListResponse, ApiMeta
from app.domain.engine.priority_models import PriorityResult
from app.application.services.priority_service import PriorityService
from app.api.dependencies import get_maintenance_service
from app.application.services.maintenance_service import MaintenanceService
from datetime import datetime, timezone
import uuid

router = APIRouter()

def _meta() -> ApiMeta:
    return ApiMeta(
        timestamp=datetime.now(timezone.utc).isoformat(),
        requestId=str(uuid.uuid4()),
        version="v1.0.0",
    )

_priority_service = PriorityService()


class EvaluateTaskRequest(BaseModel):
    task_id: str
    num_train_impacts: Optional[int] = 0


class EvaluateBatchRequest(BaseModel):
    task_ids: List[str]
    impacts_by_task: Optional[dict] = None


@router.post("/engine/priority/evaluate", response_model=ApiResponse[PriorityResult])
def evaluate_priority(
    req: EvaluateTaskRequest,
    maint_service: MaintenanceService = Depends(get_maintenance_service),
):
    """Evaluate maintenance priority for a single task."""
    task = maint_service.get_task(req.task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {req.task_id} not found.")

    # Attempt to find a linked defect from the same asset
    defect = maint_service.get_defect_for_task(req.task_id)

    result = _priority_service.evaluate_task(
        task=task,
        defect=defect,
        num_train_impacts=req.num_train_impacts or 0,
    )
    return ApiResponse(data=result, meta=_meta())


@router.post("/engine/priority/evaluate-batch", response_model=ApiListResponse[PriorityResult])
def evaluate_priority_batch(
    req: EvaluateBatchRequest,
    maint_service: MaintenanceService = Depends(get_maintenance_service),
):
    """Evaluate maintenance priority for a batch of tasks, sorted highest first."""
    tasks = []
    for task_id in req.task_ids:
        task = maint_service.get_task(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found.")
        tasks.append(task)

    defects_by_task = {
        t.task_id: maint_service.get_defect_for_task(t.task_id)
        for t in tasks
    }
    impacts = req.impacts_by_task or {}

    results = _priority_service.evaluate_tasks(
        tasks=tasks,
        defects_by_task=defects_by_task,
        impacts_by_task=impacts,
    )

    from app.api.models import PaginationMeta
    import math
    total = len(results)
    return ApiListResponse(
        data=results,
        pagination=PaginationMeta(totalItems=total, page=1, pageSize=total, totalPages=1),
        meta=_meta(),
    )