import { MaintenanceTask } from '../../maintenance/maintenance-task';
import { Defect } from '../../maintenance/defect';
import { ApiResponse, ApiListResponse } from '../common/envelope';

export type MaintenanceTaskResponse = ApiResponse<MaintenanceTask>;
export type MaintenanceTaskListResponse = ApiListResponse<MaintenanceTask>;
export type DefectResponse = ApiResponse<Defect>;
export type DefectListResponse = ApiListResponse<Defect>;
