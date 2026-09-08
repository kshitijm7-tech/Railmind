from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.domain.enums import PlanStatus, PlanStrategy, BlockStatus
from app.domain.models.common import TimeInterval, Provenance

class ObjectiveTerm(BaseModel):
    name: str
    value: float
    weight: float

class PlanMetrics(BaseModel):
    total_maintenance_time_minutes: float
    total_train_delay_minutes: float
    constraints_violated: int
    resource_utilization_percent: float
    objective_terms: Optional[List[ObjectiveTerm]] = None
    overall_score: Optional[float] = None

class PlanVersion(BaseModel):
    version: int
    created_at: str
    author: str
    changes_summary: str

class Block(BaseModel):
    block_id: str
    section_id: str
    interval: TimeInterval
    status: BlockStatus
    tasks: List[str]
    required_power_off: bool
    is_integrated: bool

class CandidateBlockWindow(BaseModel):
    interval: TimeInterval
    suitability_score: float
    conflicts: List[str]

class Plan(BaseModel):
    plan_id: str
    name: str
    horizon: TimeInterval
    status: PlanStatus
    strategy: PlanStrategy
    blocks: List[Block]
    metrics: PlanMetrics
    version: PlanVersion
    provenance: Provenance
