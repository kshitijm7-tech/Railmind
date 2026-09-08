from fastapi import APIRouter, Depends, Query
from app.api.models import ApiListResponse, ApiMeta, PaginationMeta
from app.domain.models.maintenance import MaintenanceTask
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
