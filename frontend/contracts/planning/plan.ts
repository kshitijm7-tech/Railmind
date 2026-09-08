import { PlanId, ISOTimestamp } from '../common/ids';
import { TimeInterval } from '../common/time';
import { Block } from './block';
import { PlanMetrics } from './plan-metrics';
import { Provenance } from '../common/provenance';

export type PlanStatus = 'DRAFT' | 'PROPOSED' | 'APPROVED' | 'ACTIVE' | 'ARCHIVED' | 'REJECTED';
export type PlanStrategy = 'MAINTENANCE_MAXIMIZED' | 'OPERATIONS_MAXIMIZED' | 'BALANCED';

export interface PlanVersion {
  readonly version: number;
  readonly created_at: ISOTimestamp;
  readonly author: string;
  readonly changes_summary: string;
}

export interface Plan {
  readonly plan_id: PlanId;
  readonly name: string;
  readonly horizon: TimeInterval;
  readonly status: PlanStatus;
  readonly strategy: PlanStrategy;
  readonly blocks: Block[];
  readonly metrics: PlanMetrics;
  readonly version: PlanVersion;
  readonly provenance: Provenance;
}
