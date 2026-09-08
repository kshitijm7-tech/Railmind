from fastapi import APIRouter, Depends, Query, HTTPException
from app.api.models import ApiListResponse, ApiResponse, ApiMeta, PaginationMeta
from app.domain.models.infrastructure import RailwayAsset, TrackSection, Corridor
from app.application.services.infrastructure_service import InfrastructureService
from app.api.dependencies import get_infrastructure_service
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

@router.get("/assets", response_model=ApiListResponse[RailwayAsset])
def get_assets(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: InfrastructureService = Depends(get_infrastructure_service)
):
    items, total = service.get_assets(page, page_size)
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    return ApiListResponse(
        data=items,
        pagination=PaginationMeta(totalItems=total, page=page, pageSize=page_size, totalPages=total_pages),
        meta=get_meta()
    )

@router.get("/assets/{asset_id}", response_model=ApiResponse[RailwayAsset])
def get_asset(
    asset_id: str,
    service: InfrastructureService = Depends(get_infrastructure_service)
):
    item = service.get_asset(asset_id)
    if not item:
        raise HTTPException(status_code=404, detail="Asset not found")
    return ApiResponse(data=item, meta=get_meta())

@router.get("/track-sections", response_model=ApiListResponse[TrackSection])
def get_track_sections(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: InfrastructureService = Depends(get_infrastructure_service)
):
    items, total = service.get_track_sections(page, page_size)
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    return ApiListResponse(
        data=items,
        pagination=PaginationMeta(totalItems=total, page=page, pageSize=page_size, totalPages=total_pages),
        meta=get_meta()
    )

@router.get("/track-sections/{section_id}", response_model=ApiResponse[TrackSection])
def get_track_section(
    section_id: str,
    service: InfrastructureService = Depends(get_infrastructure_service)
):
    item = service.get_track_section(section_id)
    if not item:
        raise HTTPException(status_code=404, detail="Track section not found")
    return ApiResponse(data=item, meta=get_meta())

@router.get("/corridors", response_model=ApiListResponse[Corridor])
def get_corridors(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: InfrastructureService = Depends(get_infrastructure_service)
):
    items, total = service.get_corridors(page, page_size)
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    return ApiListResponse(
        data=items,
        pagination=PaginationMeta(totalItems=total, page=page, pageSize=page_size, totalPages=total_pages),
        meta=get_meta()
    )

@router.get("/corridors/{corridor_id}", response_model=ApiResponse[Corridor])
def get_corridor(
    corridor_id: str,
    service: InfrastructureService = Depends(get_infrastructure_service)
):
    item = service.get_corridor(corridor_id)
    if not item:
        raise HTTPException(status_code=404, detail="Corridor not found")
    return ApiResponse(data=item, meta=get_meta())
