from fastapi import APIRouter, Depends, Query, Path
from typing import List
from app.api.models import ApiListResponse, ApiResponse, ApiMeta, PaginationMeta, GeneratePlanRequest, AsyncJob, ComparePlansRequest, ComparePlansResponse
from app.domain.models.planning import Plan, Block, PlanMetrics, PlanVersion, CandidateBlockWindow
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

@router.get("/plans/{id}", response_model=ApiResponse[Plan])
def get_plan(
    id: str = Path(...),
    service: PlanningService = Depends(get_planning_service)
):
    plan = service.get_plan(id)
    return ApiResponse(
        data=plan,
        meta=get_meta()
    )

@router.get("/plans/{id}/versions", response_model=ApiListResponse[PlanVersion])
def get_plan_versions(
    id: str = Path(...),
    service: PlanningService = Depends(get_planning_service)
):
    plan = service.get_plan(id)
    versions = [plan.version] if plan else []
    return ApiListResponse(
        data=versions,
        pagination=PaginationMeta(totalItems=len(versions), page=1, pageSize=10, totalPages=1),
        meta=get_meta()
    )

@router.get("/plans/{id}/metrics", response_model=ApiResponse[PlanMetrics])
def get_plan_metrics(
    id: str = Path(...),
    service: PlanningService = Depends(get_planning_service)
):
    plan = service.get_plan(id)
    metrics = plan.metrics if plan else None
    return ApiResponse(
        data=metrics,
        meta=get_meta()
    )

@router.post("/planning/generate", response_model=AsyncJob, status_code=202)
def generate_plan(
    request: GeneratePlanRequest,
    service: PlanningService = Depends(get_planning_service)
):
    return service.generate_plan(request)

@router.get("/planning/candidates", response_model=ApiListResponse[CandidateBlockWindow])
def get_candidates(
    service: PlanningService = Depends(get_planning_service)
):
    return ApiListResponse(
        data=[],
        pagination=PaginationMeta(totalItems=0, page=1, pageSize=10, totalPages=0),
        meta=get_meta()
    )

@router.get("/planning/blocks", response_model=ApiListResponse[Block])
def get_blocks(
    service: PlanningService = Depends(get_planning_service)
):
    return ApiListResponse(
        data=[],
        pagination=PaginationMeta(totalItems=0, page=1, pageSize=10, totalPages=0),
        meta=get_meta()
    )

@router.post("/plans/compare", response_model=ComparePlansResponse)
def compare_plans(
    request: ComparePlansRequest,
    service: PlanningService = Depends(get_planning_service)
):
    return service.compare_plans(request.planIds)
