from typing import Optional
from pydantic import BaseModel
from app.domain.enums import Criticality, Department, TaskType, TaskStatus
from app.domain.models.common import TimeInterval, DurationMinutes

class PriorityBreakdown(BaseModel):
    safetyScore: int
    operationalImpact: int
    maintenanceBacklog: int
    resourceAvailability: int

class MaintenanceTask(BaseModel):
    task_id: str
    asset_id: str
    section_id: str
    type: TaskType
    status: TaskStatus
    criticality: Criticality
    department: Department
    description: str
    requested_window: Optional[TimeInterval] = None
    duration: DurationMinutes
    requires_power_block: bool
    requires_traffic_block: bool
    priority_breakdown: Optional[PriorityBreakdown] = None
