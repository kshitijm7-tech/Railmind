from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
from app.domain.models.recovery import RecoveryAssessmentRequest, RecoveryAssessmentResult
from app.application.services.recovery_service import RecoveryService

router = APIRouter()
recovery_service = RecoveryService()

class RecoveryPayload(BaseModel):
    request: RecoveryAssessmentRequest
    raw_context: Dict[str, Any] = {}

@router.post("/assess", response_model=RecoveryAssessmentResult)
def assess_recovery(payload: RecoveryPayload):
    """
    Evaluates a disruption, determines impact across trains, maintenance, and infrastructure,
    and generates feasible recovery candidates for further P11/P12/P17 analysis.
    """
    try:
        result = recovery_service.assess_recovery(
            payload.request, 
            payload.raw_context
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))