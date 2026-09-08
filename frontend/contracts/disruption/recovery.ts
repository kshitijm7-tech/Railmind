import { RecoveryPlanId, DisruptionId, BlockId, TaskId, TrainId, ISOTimestamp } from '../common/ids';
import { Provenance } from '../common/provenance';

export type RecoveryActionType = 
  | 'RESCHEDULE_BLOCK'
  | 'SHORTEN_BLOCK'
  | 'MOVE_BLOCK'
  | 'CANCEL_BLOCK'
  | 'REROUTE_TRAIN'
  | 'DEFER_TASK'
  | 'RESEQUENCE_TASKS';

export interface RecoveryAction {
  readonly action_type: RecoveryActionType;
  readonly target_block_id?: BlockId;
  readonly target_task_id?: TaskId;
  readonly target_train_id?: TrainId;
  readonly description: string;
  readonly estimated_delay_reduction_min: number;
}

export type RecoveryStatus = 'PROPOSED' | 'EVALUATING' | 'APPROVED' | 'EXECUTING' | 'COMPLETED' | 'REJECTED';

export interface RecoveryPlan {
  readonly recovery_plan_id: RecoveryPlanId;
  readonly disruption_id: DisruptionId;
  readonly actions: RecoveryAction[];
  readonly status: RecoveryStatus;
  readonly generated_at: ISOTimestamp;
  readonly provenance: Provenance;
}

export interface RecoveryCandidate {
  readonly candidate_id: string;
  readonly recovery_plan_id: RecoveryPlanId;
  readonly estimated_recovery_time_min: number;
  readonly confidence: number;
  readonly trade_offs: string[];
}
