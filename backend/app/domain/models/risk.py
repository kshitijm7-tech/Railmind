from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

from app.domain.models.common import Provenance, TimeInterval
from app.domain.enums import DataState

class RiskType(str, Enum):
    ASSET_FAILURE = "ASSET_FAILURE"
    SERVICE_DISRUPTION = "SERVICE_DISRUPTION"
    TRAIN_DELAY = "TRAIN_DELAY"
    MAINTENANCE_OVERRUN = "MAINTENANCE_OVERRUN"
    ASSET_AVAILABILITY = "ASSET_AVAILABILITY"
    OPERATIONAL_CONGESTION = "OPERATIONAL_CONGESTION"

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class RiskQualityLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INSUFFICIENT = "INSUFFICIENT"

class RiskQuality(BaseModel):
    level: RiskQualityLevel
    dimensions: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)

class RiskFactor(BaseModel):
    factor_id: str
    factor_type: str
    raw_value: float
    normalized_value: float
    weight: float
    contribution: float
    direction: int  # 1 for increasing risk, -1 for decreasing
    explanation: str

class RiskPredictionRequest(BaseModel):
    request_id: str
    target_type: RiskType
    target_id: str
    horizon: TimeInterval
    state_mode: DataState = DataState.LIVE
    scenario_id: Optional[str] = None
    requested_at: datetime
    # Optionally supply known context or let service fetch it
    forecast_id_ref: Optional[str] = None
    priority_id_ref: Optional[str] = None

class RiskPredictionResult(BaseModel):
    risk_id: str
    request: RiskPredictionRequest
    
    risk_level: RiskLevel
    risk_score: float # Heuristic 0-100, not a probability unless calibrated
    probability: Optional[float] = None
    impact: Optional[float] = None
    
    factors: List[RiskFactor]
    explanation: str
    quality: RiskQuality
    provenance: Provenance
    
    model_name: str
    model_version: str
    feature_version: str
    engine_version: str
    
    generated_at: datetime