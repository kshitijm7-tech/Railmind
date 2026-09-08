from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

from app.domain.models.common import TimeInterval, Provenance
from app.domain.enums import DataState

class ForecastTargetType(str, Enum):
    TRAIN_DEMAND = "TRAIN_DEMAND"
    MAINTENANCE_WORKLOAD = "MAINTENANCE_WORKLOAD"
    OPERATIONAL_PRESSURE = "OPERATIONAL_PRESSURE"

class ForecastScope(str, Enum):
    CORRIDOR = "CORRIDOR"
    SECTION = "SECTION"
    NETWORK = "NETWORK"

class ForecastQualityLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INSUFFICIENT = "INSUFFICIENT"

class ForecastQuality(BaseModel):
    score: float
    level: ForecastQualityLevel
    dimensions: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)

class ForecastRequest(BaseModel):
    request_id: str
    target_type: ForecastTargetType
    scope: ForecastScope
    scope_id: Optional[str] = None
    horizon: TimeInterval
    granularity_minutes: int
    state_mode: DataState = DataState.LIVE
    scenario_id: Optional[str] = None
    requested_at: datetime

class ForecastObservation(BaseModel):
    timestamp: datetime
    predicted_value: float
    lower_bound: float
    upper_bound: float
    confidence: float

class ForecastResult(BaseModel):
    forecast_id: str
    request: ForecastRequest
    predictions: List[ForecastObservation]
    
    model_name: str
    model_version: str
    feature_version: str
    engine_version: str
    
    quality: ForecastQuality
    provenance: Provenance
    explanation: str
    
    historical_window: Optional[TimeInterval] = None
    generated_at: datetime