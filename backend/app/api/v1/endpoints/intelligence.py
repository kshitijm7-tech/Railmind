from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
from app.domain.models.intelligence import DecisionIntelligenceRequest, DecisionIntelligenceResult
from app.application.services.intelligence_service import DecisionIntelligenceService

router = APIRouter()
intelligence_service = DecisionIntelligenceService()

class IntelligencePayload(BaseModel):
    request: DecisionIntelligenceRequest
    raw_context: Dict[str, Any] = {}

@router.post("/evaluate", response_model=DecisionIntelligenceResult)
def evaluate_decision_intelligence(payload: IntelligencePayload):
    """
    Synthesize Priority, Risk, Forecast, and Simulation evidence to evaluate
    and recommend candidate plans.
    """
    try:
        result = intelligence_service.generate_intelligence(
            payload.request, 
            payload.raw_context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))