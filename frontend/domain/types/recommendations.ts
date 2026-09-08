export interface ObjectiveTerm {
  name: string;
  weight: number;
  value: number;
  weighted_contribution: number;
  description: string;
}

export interface ConstraintTraceItem {
  constraint_name: string;
  category: 'Safety' | 'Resource' | 'Possession' | 'Precedence' | 'Window' | 'Operational';
  status: 'SATISFIED' | 'TIGHT' | 'VIOLATED' | 'RELAXED';
  details: string;
}

export interface PlanAlternativeSummary {
  plan_id: string;
  name: string;
  strategy: string;
  delay_delta_min: number;
  tasks_delta: number;
  risk_delta_pct: number;
  recommendation_rank: number;
}

export interface EvidenceItem {
  source: 'ML_DURATION' | 'ML_DELAY' | 'PRIORITY_SCORE' | 'MONTE_CARLO';
  label: string;
  value: string | number;
  confidence: number;
  model_version: string;
}

export interface Recommendation {
  recommendation_id: string;
  state_version: string;
  plan_id: string;
  plan_name: string;
  model_version: string;
  headline: string;
  action_summary: string;
  primary_rationale: string;
  expected_outcome: {
    total_delay_min: number;
    affected_trains_count: number;
    maintenance_completion_pct: number;
    overrun_risk_pct: number;
  };
  objective_breakdown: ObjectiveTerm[];
  constraint_trace: ConstraintTraceItem[];
  alternatives: PlanAlternativeSummary[];
  evidence: EvidenceItem[];
  created_at: string;
  status: 'PENDING_REVIEW' | 'APPROVED' | 'MODIFIED' | 'REJECTED';
}
