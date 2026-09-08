from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.domain.enums import Criticality, Department, TaskType, TaskStatus, DefectStatus, DefectSource, DefectSeverity
from app.domain.models.common import TimeInterval, DurationMinutes, Provenance

class PriorityBreakdown(BaseModel):
    safety_score: int
    reliability_score: int
    efficiency_score: int
    total_score: int

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

class Defect(BaseModel):
    defect_id: str
    asset_id: str
    section_id: str
    defect_type: str
    description: str
    severity: DefectSeverity
    criticality: Criticality
    detected_at: datetime
    detected_by: DefectSource
    operational_impact: str
    is_safety_critical: bool
    urgency_hours: int
    status: DefectStatus
    linked_task_id: Optional[str] = None
    department: Department
    provenance: Provenance
