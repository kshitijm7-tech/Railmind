from fastapi import APIRouter
from app.api.models import ApiResponse, ApiMeta
from datetime import datetime, timezone
import uuid

router = APIRouter()
root_router = APIRouter()

def get_meta() -> ApiMeta:
    return ApiMeta(
        timestamp=datetime.now(timezone.utc).isoformat(),
        requestId=str(uuid.uuid4()),
        version="v1.0.0"
    )

@root_router.get("/health", response_model=ApiResponse[str])
def health_check():
    return ApiResponse(
        data="OK",
        meta=get_meta()
    )

@router.get("/version", response_model=ApiResponse[dict])
def get_version():
    return ApiResponse(
        data={"version": "1.0.0"},
        meta=get_meta()
    )
