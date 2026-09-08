import { ISOTimestamp } from '../../contracts/common/ids';
﻿import { Block } from './blocks';

export type PlanStatus = 'Draft' | 'Generating' | 'Generated' | 'Simulated' | 'Recommended' | 'Approved' | 'Rejected' | 'Invalidated' | 'Superseded';

export interface PlanMetrics {
  total_delay_minutes: number;
  passenger_trains_affected: number;
  goods_trains_affected: number;
  maintenance_tasks_completed: number;
  maintenance_tasks_unscheduled: number;
  blocks_count: number;
  bundled_blocks_count: number;
  overall_overrun_risk: number; // 0.0 to 1.0 (Monte Carlo P(violation))
  objective_score: number;
}

export interface Plan {
  plan_id: string;
  name: string;
  version: number;
  state_version: string;
  strategy: 'Maintenance Priority' | 'Operations Priority' | 'Balanced' | 'Robust / Risk-Aware';
  status: PlanStatus;
  blocks: Block[];
  metrics: PlanMetrics;
  created_at: ISOTimestamp;
  solver_runtime_ms: number;
}
