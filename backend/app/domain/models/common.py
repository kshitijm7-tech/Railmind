from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.domain.enums import DataState, DataSource

class TimeInterval(BaseModel):
    startTime: datetime
    endTime: datetime

class DurationMinutes(BaseModel):
    value: int

class Provenance(BaseModel):
    state: DataState
    source: DataSource
    generatedAt: datetime
    generatorVersion: Optional[str] = None
