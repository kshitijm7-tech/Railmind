from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

class AuditEvent(BaseModel):
    event_id: str
    decision_id: str
    action: str
    actor: str
    role: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: str
