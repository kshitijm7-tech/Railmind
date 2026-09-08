from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
from app.domain.enums import DecisionStatus

class Approval(BaseModel):
    approver: str
    role: str
    timestamp: datetime
    comments: Optional[str] = None

class Decision(BaseModel):
    decision_id: str
    recommendation_id: str
    target_plan_id: str
    target_plan_version: str
    status: DecisionStatus
    action_taken: str
    approvals: List[Approval] = Field(default_factory=list)
    recorded_at: datetime
    justification: Optional[str] = None
    audit_history: List[str] = Field(default_factory=list)

class ApproveDecisionBody(BaseModel):
    approver: str
    role: str
    justification: str
    comments: Optional[str] = None

class RejectDecisionBody(BaseModel):
    approver: str
    role: str
    reason: str

class DeferDecisionBody(BaseModel):
    approver: str
    role: str
    reason: str
    deferUntil: Optional[datetime] = None

