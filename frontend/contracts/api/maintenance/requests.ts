import { TaskId, AssetId, SectionId, DefectId, ISOTimestamp } from '../../common/ids';
import { Criticality, Department } from '../../common/enums';
import { PaginationParams, SortParams, DateRangeFilter, ScenarioContext } from '../common/envelope';
import { TaskType, TaskStatus } from '../../maintenance/maintenance-task';
import { DefectStatus } from '../../maintenance/defect';
import { TimeInterval, DurationMinutes } from '../../common/time';

export interface MaintenanceTaskListQuery extends PaginationParams, SortParams, DateRangeFilter {
  readonly status?: TaskStatus;
  readonly department?: Department;
  readonly criticality?: Criticality;
  readonly sectionId?: SectionId;
  readonly assetId?: AssetId;
  readonly taskType?: TaskType;
  readonly overdueOnly?: boolean;
  readonly scenarioContext?: ScenarioContext;
}

export interface CreateMaintenanceTaskBody {
  readonly assetId: AssetId;
  readonly sectionId: SectionId;
  readonly type: TaskType;
  readonly criticality: Criticality;
  readonly department: Department;
  readonly description: string;
  readonly requestedWindow: TimeInterval;
  readonly duration: DurationMinutes;
  readonly requiresPowerBlock: boolean;
  readonly requiresTrafficBlock: boolean;
}

export interface UpdateMaintenanceTaskBody {
  readonly status?: TaskStatus;
  readonly description?: string;
  readonly requestedWindow?: TimeInterval;
  readonly duration?: DurationMinutes;
}

export interface DefectListQuery extends PaginationParams, SortParams {
  readonly assetId?: AssetId;
  readonly sectionId?: SectionId;
  readonly status?: DefectStatus;
  readonly linkedTaskId?: TaskId;
  readonly from?: ISOTimestamp;
  readonly to?: ISOTimestamp;
}

export interface CreateDefectBody {
  readonly assetId: AssetId;
  readonly sectionId: SectionId;
  readonly defectType: string;
  readonly description: string;
  readonly isSafetyCritical: boolean;
  readonly urgencyHours: number;
  readonly department: Department;
}
