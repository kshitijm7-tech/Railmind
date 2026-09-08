import { Criticality, Department } from '../../contracts/common/enums';

export type TaskType = 'Preventive' | 'Corrective' | 'Inspection' | 'Defect';

export type TaskStatus = 'Pending' | 'Scheduled' | 'In Progress' | 'Completed' | 'Overdue' | 'Blocked' | 'Cancelled';

export interface DurationEstimate {
  expected_min: number;
  p10_min: number;
  p90_min: number;
  overrun_probability: number; // 0.0 to 1.0
  confidence: number;
}

export interface MaintenanceTask {
  task_id: string;
  title: string;
  section_id: string;
  asset_id?: string;
  department: Department;
  task_type: TaskType;
  expected_duration_min: number;
  duration_estimates: DurationEstimate;
  crew_size_required: number;
  crew_qualification: Department;
  criticality: Criticality;
  overdue_days: number;
  dependency_task_ids: string[];
  earliest_start: string;
  latest_finish?: string;
  priority_score: number; // 0.0 - 100.0 computed by scoring / ML
  priority_breakdown?: {
    criticality_score: number;
    overdue_factor: number;
    failure_risk: number;
    safety_flag: number;
    downstream_impact: number;
  };
  status: TaskStatus;
}
