import { Criticality } from './network';

export type DisruptionType = 'BLOCK_OVERRUN' | 'TRACK_UNAVAILABLE' | 'SIGNAL_FAILURE' | 'OHE_BREAKDOWN' | 'UNSCHEDULED_TRAIN';

export type IncidentStatus = 'Detected' | 'Assessing' | 'Impact Identified' | 'Recovery Proposed' | 'Recovery Approved' | 'Resolved';

export interface Incident {
  incident_id: string;
  incident_type: DisruptionType;
  title: string;
  section_id: string;
  station_id?: string;
  severity: Criticality;
  status: IncidentStatus;
  detected_at: string;
  estimated_resolution_time: string;
  affected_plan_id?: string;
  affected_train_ids: string[];
  affected_block_ids: string[];
  description: string;
  recovery_plan_id?: string;
}
