import { DecisionId, RecommendationId, ISOTimestamp } from '../common/ids';

export type DecisionStatus = 'PENDING' | 'APPROVED' | 'REJECTED' | 'SUPERSEDED';

export interface Approval {
  readonly approver: string;
  readonly role: string;
  readonly timestamp: ISOTimestamp;
  readonly comments?: string;
}

export interface Decision {
  readonly decision_id: DecisionId;
  readonly recommendation_id: RecommendationId;
  readonly status: DecisionStatus;
  readonly action_taken: string;
  readonly approvals: Approval[];
  readonly recorded_at: ISOTimestamp;
  readonly justification?: string;
}
