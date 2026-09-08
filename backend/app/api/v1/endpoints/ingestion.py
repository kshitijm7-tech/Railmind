from fastapi import APIRouter, Depends, HTTPException
from app.infrastructure.integrations.models import DataSourceType, IngestionBatch
from app.infrastructure.integrations.service import IngestionService
import uuid

router = APIRouter()
ingestion_service = IngestionService()

@router.post("/{source}", response_model=IngestionBatch)
def trigger_ingestion(source: DataSourceType):
    """
    Trigger a deterministic mock ingestion batch for the given source type.
    """
    correlation_id = f"CORR-{uuid.uuid4().hex[:8]}"
    try:
        batch = ingestion_service.run_ingestion(source, correlation_id)
        return batch
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))