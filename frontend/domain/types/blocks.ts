import { Department } from './network';

export type BlockStatus = 'Requested' | 'Approved' | 'Active' | 'Completed' | 'Overrun' | 'Cancelled';

export interface CandidateBlockWindow {
  window_id: string;
  section_id: string;
  earliest_start: string;
  latest_end: string;
  max_duration_min: number;
  conflicting_train_ids: string[];
  recommended_usage: 'NIGHT_POSSESSION' | 'DAY_LIGHT_WINDOW' | 'SHADOW_BLOCK';
}

export interface Block {
  block_id: string;
  section_id: string;
  start_time: string;
  end_time: string;
  duration_min: number;
  assigned_task_ids: string[];
  departments_involved: Department[];
  is_bundled: boolean;
  status: BlockStatus;
  plan_version: number;
  actual_start_time?: string;
  actual_end_time?: string;
  overrun_min?: number;
  affected_train_ids: string[];
}
