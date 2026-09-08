import uuid
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import HTTPException

from app.domain.models.decision import Decision, ApproveDecisionBody, RejectDecisionBody, DeferDecisionBody, Approval
from app.domain.models.audit import AuditEvent
from app.domain.enums import DecisionStatus
from app.infrastructure.in_memory_decision_repository import InMemoryDecisionRepository, InMemoryAuditRepository
from app.infrastructure.in_memory_plan_repository import InMemoryPlanRepository

class DecisionService:
    def __init__(
        self,
        decision_repo: InMemoryDecisionRepository,
        audit_repo: InMemoryAuditRepository,
        plan_repo: InMemoryPlanRepository
    ):
        self.decision_repo = decision_repo
        self.audit_repo = audit_repo
        self.plan_repo = plan_repo

    def get_all_decisions(self) -> List[Decision]:
        return self.decision_repo.get_all()

    def get_decision(self, decision_id: str) -> Optional[Decision]:
        return self.decision_repo.get_by_id(decision_id)

    def _validate_decision_and_plan(self, decision_id: str) -> Decision:
        decision = self.decision_repo.get_by_id(decision_id)
        if not decision:
            raise HTTPException(status_code=404, detail="Decision not found")
        
        plan = self.plan_repo.get_by_id(decision.target_plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Target plan not found")
            
        if decision.status != DecisionStatus.PENDING:
            raise HTTPException(status_code=400, detail="Decision is not in PENDING state")
            
        return decision

    def _record_audit(self, decision: Decision, action: str, actor: str, role: str, details: str):
        event = AuditEvent(
            event_id=f"AUDIT-{uuid.uuid4()}",
            decision_id=decision.decision_id,
            action=action,
            actor=actor,
            role=role,
            timestamp=datetime.now(timezone.utc),
            details=details
        )
        self.audit_repo.save(event)
        decision.audit_history.append(event.event_id)

    def approve_decision(self, decision_id: str, body: ApproveDecisionBody) -> Decision:
        decision = self._validate_decision_and_plan(decision_id)
        
        approval = Approval(
            approver=body.approver,
            role=body.role,
            timestamp=datetime.now(timezone.utc),
            comments=body.comments
        )
        decision.approvals.append(approval)
        decision.status = DecisionStatus.APPROVED
        decision.action_taken = "Plan Approved"
        decision.justification = body.justification
        
        self._record_audit(decision, "PLAN_APPROVED", body.approver, body.role, body.justification)
        
        return self.decision_repo.save(decision)

    def reject_decision(self, decision_id: str, body: RejectDecisionBody) -> Decision:
        decision = self._validate_decision_and_plan(decision_id)
        
        decision.status = DecisionStatus.REJECTED
        decision.action_taken = "Plan Rejected"
        decision.justification = body.reason
        
        self._record_audit(decision, "PLAN_REJECTED", body.approver, body.role, body.reason)
        
        return self.decision_repo.save(decision)

    def defer_decision(self, decision_id: str, body: DeferDecisionBody) -> Decision:
        decision = self._validate_decision_and_plan(decision_id)
        
        decision.status = DecisionStatus.DEFERRED
        decision.action_taken = "Plan Deferred"
        decision.justification = body.reason
        
        details = body.reason
        if body.deferUntil:
            details += f" (Deferred until {body.deferUntil.isoformat()})"
            
        self._record_audit(decision, "PLAN_DEFERRED", body.approver, body.role, details)
        
        return self.decision_repo.save(decision)
