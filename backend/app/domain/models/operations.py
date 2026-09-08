from typing import List, Optional
from pydantic import BaseModel
from app.domain.models.common import ScheduledTiming, TimeInterval
from app.domain.enums import TrainType, TrainStatus, RiskLevel, ImpactType, WindowAvailability

class SectionTiming(BaseModel):
    section_id: str
    entry_time: ScheduledTiming
    exit_time: ScheduledTiming

class TrainService(BaseModel):
    train_id: str
    name: str
    train_number: str
    type: TrainType
    origin_station_id: str
    destination_station_id: str
    sections: List[SectionTiming]

class Train(BaseModel):
    service: TrainService
    max_speed_kmh: int
    length_m: int
    weight_t: int
    priority: int

class PathConstraint(BaseModel):
    type: str
    description: str

class PathSegment(BaseModel):
    section_id: str
    interval: TimeInterval
    is_conflicted: bool

class TrainPath(BaseModel):
    train_id: str
    segments: List[PathSegment]
    constraints: List[PathConstraint]
    is_valid: bool

class OperationalWindow(BaseModel):
    window_id: str
    section_id: str
    interval: TimeInterval
    availability: WindowAvailability
    max_trains: int
    currently_assigned_trains: int

class TrainImpact(BaseModel):
    train_id: str
    block_id: str
    impact_type: ImpactType
    delay_minutes: int
    is_rerouted: bool
    is_cancelled: bool
    reroute_description: Optional[str] = None
    severity: RiskLevel
    reason: str
    cascading_delay_minutes: int
