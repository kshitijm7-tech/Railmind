from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.domain.enums import DataState, DataSource

class TimeInterval(BaseModel):
    start: datetime
    end: datetime

class DurationMinutes(BaseModel):
    expected: int
    minimum: int
    maximum: int

class ScheduledTiming(BaseModel):
    scheduled: datetime
    actual: Optional[datetime] = None
    delayMinutes: int

class Provenance(BaseModel):
    state: DataState
    source: DataSource
    generatedAt: datetime
    generatorVersion: Optional[str] = None
