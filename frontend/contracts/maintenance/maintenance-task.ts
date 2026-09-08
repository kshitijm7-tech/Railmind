import { TaskId, AssetId, SectionId } from '../common/ids';
import { Criticality, Department } from '../common/enums';
import { TimeInterval, DurationMinutes } from '../common/time';

export type TaskType = 'PREVENTIVE' | 'CORRECTIVE' | 'INSPECTION' | 'EMERGENCY';
export type TaskStatus = 'PENDING' | 'SCHEDULED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';

export interface PriorityBreakdown {
  readonly safety_score: number;
  readonly reliability_score: number;
  readonly efficiency_score: number;
  readonly total_score: number;
}

export interface MaintenanceTask {
  readonly task_id: TaskId;
  readonly asset_id: AssetId;
  readonly section_id: SectionId;
  readonly type: TaskType;
  readonly status: TaskStatus;
  readonly criticality: Criticality;
  readonly department: Department;
  readonly description: string;
  readonly requested_window: TimeInterval;
  readonly duration: DurationMinutes;
  readonly requires_power_block: boolean;
  readonly requires_traffic_block: boolean;
  readonly priority_breakdown?: PriorityBreakdown;
}
