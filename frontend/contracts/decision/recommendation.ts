import { RecommendationId, PlanId, ISOTimestamp } from '../common/ids';
import { PlanMetrics } from '../planning/plan-metrics';

export interface EvidenceItem {
  readonly source: string;
  readonly description: string;
  readonly confidence: number;
}

export interface ConstraintTraceItem {
  readonly constraint_id: string;
  readonly description: string;
  readonly is_satisfied: boolean;
}

export interface RecommendationAlternative {
  readonly alternative_id: string;
  readonly plan_id: PlanId;
  readonly description: string;
  readonly metrics: PlanMetrics;
  readonly trade_offs: string[];
}

export interface Recommendation {
  readonly recommendation_id: RecommendationId;
  readonly target_plan_id: PlanId;
  readonly title: string;
  readonly rationale: string;
  readonly generated_at: ISOTimestamp;
  readonly evidence: EvidenceItem[];
  readonly constraint_traces: ConstraintTraceItem[];
  readonly alternatives: RecommendationAlternative[];
}
