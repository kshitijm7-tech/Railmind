from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import List, Optional
from datetime import datetime, timezone
import uuid

from app.api.dependencies import get_decision_service
from app.application.services.decision_service import DecisionService
from app.domain.models.decision import Decision, ApproveDecisionBody, RejectDecisionBody, DeferDecisionBody
from app.api.models import ApiResponse, ApiListResponse, ApiMeta, PaginationMeta, ApiError
from app.domain.enums import DecisionStatus

router = APIRouter()

def get_meta() -> ApiMeta:
    return ApiMeta(
        timestamp=datetime.now(timezone.utc).isoformat(),
        requestId=str(uuid.uuid4()),
        version="v1"
    )

@router.get("/decisions", response_model=ApiListResponse[Decision])
def get_decisions(
    service: DecisionService = Depends(get_decision_service),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1)
):
    decisions = service.get_all_decisions()
    
    # Simple pagination
    start = (page - 1) * page_size
    end = start + page_size
    paginated_decisions = decisions[start:end]
    
    return ApiListResponse(
        data=paginated_decisions,
        pagination=PaginationMeta(
            totalItems=len(decisions),
            page=page,
            pageSize=page_size,
            totalPages=(len(decisions) + page_size - 1) // page_size
        ),
        meta=get_meta()
    )

@router.get("/decisions/{id}", response_model=ApiResponse[Decision])
def get_decision_by_id(
    id: str = Path(...),
    service: DecisionService = Depends(get_decision_service)
):
    decision = service.get_decision(id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
        
    return ApiResponse(
        data=decision,
        meta=get_meta()
    )

@router.post("/decisions/{id}/approve", response_model=ApiResponse[Decision])
def approve_decision(
    body: ApproveDecisionBody,
    id: str = Path(...),
    service: DecisionService = Depends(get_decision_service)
):
    try:
        decision = service.approve_decision(id, body)
        return ApiResponse(data=decision, meta=get_meta())
    except HTTPException as e:
        return ApiResponse(
            meta=get_meta(),
            error=ApiError(code="HTTP_ERROR", message=e.detail, httpStatus=e.status_code)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/decisions/{id}/reject", response_model=ApiResponse[Decision])
def reject_decision(
    body: RejectDecisionBody,
    id: str = Path(...),
    service: DecisionService = Depends(get_decision_service)
):
    try:
        decision = service.reject_decision(id, body)
        return ApiResponse(data=decision, meta=get_meta())
    except HTTPException as e:
        return ApiResponse(
            meta=get_meta(),
            error=ApiError(code="HTTP_ERROR", message=e.detail, httpStatus=e.status_code)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/decisions/{id}/defer", response_model=ApiResponse[Decision])
def defer_decision(
    body: DeferDecisionBody,
    id: str = Path(...),
    service: DecisionService = Depends(get_decision_service)
):
    try:
        decision = service.defer_decision(id, body)
        return ApiResponse(data=decision, meta=get_meta())
    except HTTPException as e:
        return ApiResponse(
            meta=get_meta(),
            error=ApiError(code="HTTP_ERROR", message=e.detail, httpStatus=e.status_code)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
