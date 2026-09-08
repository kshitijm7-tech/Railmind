from typing import List, Optional, Dict
from app.domain.models.decision import Decision
from app.domain.models.audit import AuditEvent

from datetime import datetime, timezone
from app.domain.enums import DecisionStatus

class InMemoryDecisionRepository:
    def __init__(self):
        self._decisions: Dict[str, Decision] = {
            "DEC-001": Decision(
                decision_id="DEC-001",
                recommendation_id="REC-001",
                target_plan_id="PLAN-001",
                target_plan_version="1",
                status=DecisionStatus.PENDING,
                action_taken="None",
                recorded_at=datetime.now(timezone.utc)
            )
        }


    def get_all(self) -> List[Decision]:
        return list(self._decisions.values())

    def get_by_id(self, decision_id: str) -> Optional[Decision]:
        return self._decisions.get(decision_id)

    def save(self, decision: Decision) -> Decision:
        self._decisions[decision.decision_id] = decision
        return decision

class InMemoryAuditRepository:
    def __init__(self):
        self._events: Dict[str, AuditEvent] = {}

    def get_by_decision_id(self, decision_id: str) -> List[AuditEvent]:
        return [e for e in self._events.values() if e.decision_id == decision_id]

    def save(self, event: AuditEvent) -> AuditEvent:
        self._events[event.event_id] = event
        return event
