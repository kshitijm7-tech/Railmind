from fastapi import APIRouter, Depends, Query
from app.api.models import ApiListResponse, ApiMeta, PaginationMeta
from app.domain.models.planning import Plan
from app.application.services.planning_service import PlanningService
from app.api.dependencies import get_planning_service
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

@router.get("/plans", response_model=ApiListResponse[Plan])
def get_plans(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: PlanningService = Depends(get_planning_service)
):
    plans, total = service.get_plans(page, page_size)
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    return ApiListResponse(
        data=plans,
        pagination=PaginationMeta(
            totalItems=total,
            page=page,
            pageSize=page_size,
            totalPages=total_pages
        ),
        meta=get_meta()
    )
