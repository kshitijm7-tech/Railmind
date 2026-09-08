from typing import List
from pydantic import BaseModel
from datetime import datetime
from app.domain.enums import PlanStatus, PlanStrategy
from app.domain.models.common import TimeInterval, Provenance

class Block(BaseModel):
    blockId: str
    sectionId: str
    interval: TimeInterval
    taskIds: List[str]

class PlanMetrics(BaseModel):
    totalTasksScheduled: int
    totalDurationMinutes: int
    resourceUtilizationPct: float
    disruptionScore: float

class PlanVersion(BaseModel):
    versionNumber: int
    createdAt: datetime
    createdBy: str
    changes: str

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
