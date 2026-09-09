from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

from app.domain.models.common import Provenance, TimeInterval
from app.domain.enums import DataState

class EvidenceType(str, Enum):
    PRIORITY = "PRIORITY"
    RISK = "RISK"
    FORECAST = "FORECAST"
    CONSTRAINT = "CONSTRAINT"
    OPTIMIZATION = "OPTIMIZATION"
    SIMULATION = "SIMULATION"

class EvidenceQuality(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INSUFFICIENT = "INSUFFICIENT"

class DecisionEvidence(BaseModel):
    evidence_id: str
    evidence_type: EvidenceType
    source_reference: str
    summary_value: float
    direction: int  # 1 for positive benefit, -1 for negative impact
    severity: str
    timestamp: datetime
    provenance: Provenance
    explanation: str
    
class DecisionTradeoff(BaseModel):
    factor_name: str
    description: str
    is_strength: bool

class CandidateAssessment(BaseModel):
    plan_id: str
    rank: int
    score: float
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    tradeoffs: List[DecisionTradeoff] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)

class DecisionIntelligenceRequest(BaseModel):
    request_id: str
    decision_context: str
    candidate_plan_ids: List[str]
    horizon: TimeInterval
    state_mode: DataState = DataState.LIVE
    scenario_id: Optional[str] = None
    requested_at: datetime

class DecisionIntelligenceResult(BaseModel):
    decision_id: str
    request: DecisionIntelligenceRequest
    recommended_plan_id: Optional[str]
    candidates: List[CandidateAssessment]
    evidence: List[DecisionEvidence]
    
    quality_level: EvidenceQuality
    quality_warnings: List[str] = Field(default_factory=list)
    
    primary_drivers: List[str] = Field(default_factory=list)
    overall_explanation: str
    
    provenance: Provenance
    
    engine_name: str
    engine_version: str
    feature_version: str
    generated_at: datetime