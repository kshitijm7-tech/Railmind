import { DefectId, AssetId, SectionId, TaskId, ISOTimestamp } from '../common/ids';
import { Criticality, Department } from '../common/enums';
import { Provenance } from '../common/provenance';

export type DefectSeverity = 'MINOR' | 'MODERATE' | 'SEVERE' | 'CRITICAL';
export type DefectStatus = 'DETECTED' | 'ASSESSED' | 'LINKED' | 'RECTIFIED' | 'DEFERRED' | 'CLOSED';
export type DefectSource = 'INSPECTION' | 'AUTOMATED_MONITORING' | 'DRIVER_REPORT' | 'AEF_SCAN' | 'BDMS_IMPORT' | 'USER_REPORT';

export interface Defect {
  readonly defect_id: DefectId;
  readonly asset_id: AssetId;
  readonly section_id: SectionId;
  readonly defect_type: string;
  readonly description: string;
  readonly severity: DefectSeverity;
  readonly criticality: Criticality;
  readonly detected_at: ISOTimestamp;
  readonly detected_by: DefectSource;
  readonly operational_impact: string;
  readonly is_safety_critical: boolean;
  readonly urgency_hours: number;
  readonly status: DefectStatus;
  readonly linked_task_id?: TaskId;
  readonly department: Department;
  readonly provenance: Provenance;
}
