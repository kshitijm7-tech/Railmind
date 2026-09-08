from fastapi import APIRouter, HTTPException
from app.domain.models.forecasting import ForecastRequest, ForecastResult
from app.application.services.forecasting_service import ForecastingService

router = APIRouter()
forecasting_service = ForecastingService()

@router.post("/generate", response_model=ForecastResult)
def generate_forecast(request: ForecastRequest):
    """
    Generate a forecast based on a provided request configuration.
    """
    try:
        result = forecasting_service.generate_forecast(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))