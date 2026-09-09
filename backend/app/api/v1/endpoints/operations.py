from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from app.api.models import ApiListResponse, ApiResponse, ApiMeta, PaginationMeta
from app.domain.models.operations import Train, TrainPath, OperationalWindow, TrainImpact
from app.application.services.operations_service import OperationsService
from app.api.dependencies import get_operations_service
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

def _demo_trains_by_id():
    try:
        from app.infrastructure.railway_demo.repository import get_demo_seed_repository
        return {t["train_id"]: t for t in get_demo_seed_repository().get_trains()}
    except Exception:
        return {}

@router.get("/trains", response_model=ApiListResponse[Train])
def get_trains(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    train_type: Optional[str] = Query(None),
    priority: Optional[int] = Query(None),
    service: OperationsService = Depends(get_operations_service)
):
    items, total = service.get_trains(1, 1000)
    if status is not None or train_type is not None or priority is not None:
        demo = _demo_trains_by_id()
        if demo:
            wanted_type = (train_type or "").upper()
            filtered = []
            for t in items:
                tid = t.service.train_id
                raw = demo.get(tid)
                if raw is None:
                    continue
                if status is not None and raw.get("current_status") != status:
                    continue
                if train_type is not None and raw.get("train_type") != wanted_type and t.service.type.value != wanted_type:
                    continue
                if priority is not None and t.priority != priority:
                    continue
                filtered.append(t)
            items = filtered
            total = len(items)
    start = (page - 1) * page_size
    page_items = items[start:start + page_size]
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    return ApiListResponse(
        data=page_items,
        pagination=PaginationMeta(totalItems=total, page=page, pageSize=page_size, totalPages=total_pages),
        meta=get_meta()
    )

@router.get("/trains/{train_id}", response_model=ApiResponse[Train])
def get_train(
    train_id: str,
    service: OperationsService = Depends(get_operations_service)
):
    item = service.get_train(train_id)
    if not item:
        raise HTTPException(status_code=404, detail="Train not found")
    return ApiResponse(data=item, meta=get_meta())

@router.get("/train-paths", response_model=ApiListResponse[TrainPath])
def get_train_paths(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: OperationsService = Depends(get_operations_service)
):
    items, total = service.get_train_paths(page, page_size)
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    return ApiListResponse(
        data=items,
        pagination=PaginationMeta(totalItems=total, page=page, pageSize=page_size, totalPages=total_pages),
        meta=get_meta()
    )

@router.get("/operational-windows", response_model=ApiListResponse[OperationalWindow])
def get_operational_windows(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: OperationsService = Depends(get_operations_service)
):
    items, total = service.get_operational_windows(page, page_size)
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    return ApiListResponse(
        data=items,
        pagination=PaginationMeta(totalItems=total, page=page, pageSize=page_size, totalPages=total_pages),
        meta=get_meta()
    )

@router.get("/train-impacts", response_model=ApiListResponse[TrainImpact])
def get_train_impacts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: OperationsService = Depends(get_operations_service)
):
    items, total = service.get_train_impacts(page, page_size)
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    return ApiListResponse(
        data=items,
        pagination=PaginationMeta(totalItems=total, page=page, pageSize=page_size, totalPages=total_pages),
        meta=get_meta()
    )
