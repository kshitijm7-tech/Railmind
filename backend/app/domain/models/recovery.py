from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

from app.domain.models.common import Provenance, TimeInterval
from app.domain.enums import DataState

class DisruptionType(str, Enum):
    TRACK_FAILURE = "TRACK_FAILURE"
    ASSET_FAILURE = "ASSET_FAILURE"
    TRAIN_DELAY = "TRAIN_DELAY"
    MAINTENANCE_OVERRUN = "MAINTENANCE_OVERRUN"
    BLOCK_UNAVAILABLE = "BLOCK_UNAVAILABLE"
    OPERATIONAL_RESTRICTION = "OPERATIONAL_RESTRICTION"
    CONGESTION = "CONGESTION"
    EMERGENCY_EVENT = "EMERGENCY_EVENT"
    OTHER = "OTHER"

class DisruptionSeverity(str, Enum):
    MINOR = "MINOR"
    MAJOR = "MAJOR"
    CRITICAL = "CRITICAL"

class DisruptionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    RESOLVED = "RESOLVED"
    MITIGATED = "MITIGATED"

class RecoveryActionType(str, Enum):
    CANCEL_BLOCK = "CANCEL_BLOCK"
    SHIFT_BLOCK = "SHIFT_BLOCK"
    SHORTEN_BLOCK = "SHORTEN_BLOCK"
    EXTEND_BLOCK = "EXTEND_BLOCK"
    RESEQUENCE_BLOCKS = "RESEQUENCE_BLOCKS"
    DEFER_MAINTENANCE = "DEFER_MAINTENANCE"
    PRIORITIZE_MAINTENANCE = "PRIORITIZE_MAINTENANCE"
    REROUTE_TRAIN = "REROUTE_TRAIN"
    RESCHEDULE_TRAIN = "RESCHEDULE_TRAIN"
    REDUCE_OPERATIONAL_EXPOSURE = "REDUCE_OPERATIONAL_EXPOSURE"
    REPLAN = "REPLAN"
    NO_ACTION = "NO_ACTION"

class Disruption(BaseModel):
    disruption_id: str
    type: DisruptionType
    severity: DisruptionSeverity
    status: DisruptionStatus
    affected_resource: str
    affected_resource_type: str
    start_time: datetime
    expected_end_time: datetime
    actual_end_time: Optional[datetime] = None
    description: str
    state_mode: DataState
    scenario_id: Optional[str] = None
    reported_at: datetime
    source: str
    provenance: Provenance

class ImpactAssessment(BaseModel):
    disruption_id: str
    affected_trains: List[str] = Field(default_factory=list)
    affected_train_paths: List[str] = Field(default_factory=list)
    affected_maintenance_tasks: List[str] = Field(default_factory=list)
    affected_blocks: List[str] = Field(default_factory=list)
    affected_sections: List[str] = Field(default_factory=list)
    affected_assets: List[str] = Field(default_factory=list)
    delay_exposure_minutes: float = 0.0
    maintenance_exposure_hours: float = 0.0
    operational_exposure_score: float = 0.0
    asset_availability_exposure_score: float = 0.0
    description: str

class RecoveryAction(BaseModel):
    action_type: RecoveryActionType
    target_entity_id: str
    target_entity_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    description: str

class RecoveryOption(BaseModel):
    recovery_option_id: str
    base_plan_id: str
    disruption_id: str
    actions: List[RecoveryAction] = Field(default_factory=list)
    affected_entities: List[str] = Field(default_factory=list)
    expected_tradeoffs: List[str] = Field(default_factory=list)
    constraint_status: str # e.g. FEASIBLE, INFEASIBLE, UNKNOWN
    risk_summary: Optional[Dict[str, Any]] = None
    simulation_reference: Optional[str] = None
    decision_intelligence_reference: Optional[str] = None
    quality: str
    provenance: Provenance

class RecoveryAssessmentRequest(BaseModel):
    request_id: str
    disruption: Disruption
    base_plan_id: str
    requested_at: datetime

class RecoveryAssessmentResult(BaseModel):
    recovery_id: str
    disruption: Disruption
    impact_assessment: ImpactAssessment
    recovery_options: List[RecoveryOption] = Field(default_factory=list)
    recommended_option_id: Optional[str] = None
    quality: str
    warnings: List[str] = Field(default_factory=list)
    provenance: Provenance
    engine_version: str
    generated_at: datetime