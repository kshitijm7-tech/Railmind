from typing import List, Optional, Any, Dict
from pydantic import BaseModel
from datetime import datetime
from app.domain.models.common import TimeInterval, Provenance
from enum import Enum

class SimulationStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class EventType(str, Enum):
    SIMULATION_STARTED = "SIMULATION_STARTED"
    BLOCK_ACTIVATED = "BLOCK_ACTIVATED"
    BLOCK_RELEASED = "BLOCK_RELEASED"
    TRAIN_ENTERED_SECTION = "TRAIN_ENTERED_SECTION"
    TRAIN_EXITED_SECTION = "TRAIN_EXITED_SECTION"
    TRAIN_BLOCKED = "TRAIN_BLOCKED"
    TRAIN_DELAYED = "TRAIN_DELAYED"
    MAINTENANCE_STARTED = "MAINTENANCE_STARTED"
    MAINTENANCE_COMPLETED = "MAINTENANCE_COMPLETED"
    SIMULATION_COMPLETED = "SIMULATION_COMPLETED"

class SimulationEvent(BaseModel):
    event_id: str
    event_time: datetime
    event_type: EventType
    entity_id: Optional[str] = None
    description: str
    metadata: Dict[str, Any] = {}

class TrainSimulationState(BaseModel):
    train_id: str
    current_section: Optional[str]
    planned_position: Optional[str]
    actual_position: Optional[str]
    delay_minutes: float
    status: str  # RUNNING, WAITING, BLOCKED, COMPLETED

class SectionSimulationState(BaseModel):
    track_section_id: str
    is_available: bool
    occupied_by_trains: List[str]
    active_block: Optional[str]
    maintenance_active: bool

class SimulationMetric(BaseModel):
    name: str
    value: float
    unit: str

class SimulationResult(BaseModel):
    simulation_run_id: str
    status: SimulationStatus
    duration_seconds: float
    
    affected_trains: int
    total_delay_minutes: float
    maximum_delay_minutes: float
    average_delay_minutes: float
    
    completed_maintenance_tasks: int
    incomplete_maintenance_tasks: int
    blocked_trains: int
    affected_sections: List[str]
    block_utilization: float
    operational_impact_score: float
    
    events: List[SimulationEvent]
    explanation: str
    provenance: Provenance

class SimulationRun(BaseModel):
    simulation_run_id: str
    scenario_id: str
    plan_id: str
    plan_version: int
    status: SimulationStatus
    engine_version: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    configuration: Dict[str, Any]
    provenance: Provenance
    result: Optional[SimulationResult] = None