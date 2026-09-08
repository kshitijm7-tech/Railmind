from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
from app.domain.models.risk import RiskPredictionRequest, RiskPredictionResult
from app.application.services.risk_service import RiskPredictionService

router = APIRouter()
risk_service = RiskPredictionService()

class RiskPredictionPayload(BaseModel):
    request: RiskPredictionRequest
    raw_context: Dict[str, Any] = {}
    priority_context: Dict[str, Any] = {}
    forecast_context: Dict[str, Any] = {}

@router.post("/predict", response_model=RiskPredictionResult)
def predict_risk(payload: RiskPredictionPayload):
    """
    Generate a risk prediction based on a provided request configuration and context.
    """
    try:
        result = risk_service.generate_prediction(
            payload.request, 
            payload.raw_context, 
            payload.priority_context, 
            payload.forecast_context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))