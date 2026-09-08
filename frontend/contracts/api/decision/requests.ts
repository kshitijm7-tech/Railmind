import { ISOTimestamp } from '../../common/ids';
import { UserRole } from '../../common/enums';
import { PaginationParams, SortParams, DateRangeFilter } from '../common/envelope';
import { DecisionStatus } from '../../decision/decision';

export interface RecommendationListQuery extends PaginationParams, SortParams {
  readonly planId?: string;
  readonly status?: string;
}

export interface DecisionListQuery extends PaginationParams, SortParams, DateRangeFilter {
  readonly status?: DecisionStatus;
  readonly role?: UserRole;
}

export interface ApproveDecisionBody {
  readonly approver: string;
  readonly role: UserRole;
  readonly justification: string;
  readonly comments?: string;
}

export interface RejectDecisionBody {
  readonly approver: string;
  readonly role: UserRole;
  readonly reason: string;
}

export interface DeferDecisionBody {
  readonly approver: string;
  readonly role: UserRole;
  readonly reason: string;
  readonly deferUntil?: ISOTimestamp;
}
