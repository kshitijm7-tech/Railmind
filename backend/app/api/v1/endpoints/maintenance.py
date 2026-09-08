from fastapi import APIRouter, Depends, Query, HTTPException
from app.api.models import ApiListResponse, ApiResponse, ApiMeta, PaginationMeta
from app.domain.models.maintenance import MaintenanceTask, Defect
from app.application.services.maintenance_service import MaintenanceService
from app.api.dependencies import get_maintenance_service
from datetime import datetime, timezone
import uuid
import math

router = APIRouter()

def get_meta() -> ApiMeta:
    return ApiMeta(
        timestamp=datetime.now(timezone.utc).isoformat(),
        requestId=str(uuid.uuid4()),
        version="v1.0.0"
    )

@router.get("/tasks", response_model=ApiListResponse[MaintenanceTask])
def get_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: MaintenanceService = Depends(get_maintenance_service)
):
    tasks, total = service.get_tasks(page, page_size)
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    return ApiListResponse(
        data=tasks,
        pagination=PaginationMeta(
            totalItems=total,
            page=page,
            pageSize=page_size,
            totalPages=total_pages
        ),
        meta=get_meta()
    )

@router.get("/tasks/{task_id}", response_model=ApiResponse[MaintenanceTask])
def get_task(
    task_id: str,
    service: MaintenanceService = Depends(get_maintenance_service)
):
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return ApiResponse(
        data=task,
        meta=get_meta()
    )

@router.get("/defects", response_model=ApiListResponse[Defect])
def get_defects(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: MaintenanceService = Depends(get_maintenance_service)
):
    defects, total = service.get_defects(page, page_size)
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    return ApiListResponse(
        data=defects,
        pagination=PaginationMeta(
            totalItems=total,
            page=page,
            pageSize=page_size,
            totalPages=total_pages
        ),
        meta=get_meta()
    )

@router.get("/defects/{defect_id}", response_model=ApiResponse[Defect])
def get_defect(
    defect_id: str,
    service: MaintenanceService = Depends(get_maintenance_service)
):
    defect = service.get_defect(defect_id)
    if not defect:
        raise HTTPException(status_code=404, detail="Defect not found")
    return ApiResponse(
        data=defect,
        meta=get_meta()
    )
