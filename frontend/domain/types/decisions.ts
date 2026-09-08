export type DecisionActionType = 'APPROVE' | 'MODIFY' | 'REJECT';

export interface DecisionRecord {
  decision_id: string;
  recommendation_id: string;
  plan_id: string;
  state_version: string;
  action: DecisionActionType;
  authorized_by: string;
  user_role: 'Operations Controller' | 'Planning Officer' | 'Senior Divisional Engineer';
  timestamp: string;
  notes?: string;
  modifications?: Record<string, any>;
}

export interface AuditEvent {
  event_id: string;
  event_type: 'PLAN_GENERATED' | 'PLAN_SIMULATED' | 'DECISION_SUBMITTED' | 'DISRUPTION_DETECTED' | 'RECOVERY_GENERATED' | 'STATE_UPDATED';
  entity_id: string;
  entity_type: string;
  user: string;
  timestamp: string;
  state_version: string;
  summary: string;
  details?: Record<string, any>;
}
