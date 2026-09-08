/** F01 — Real maintenance API service (FastAPI). */
import { apiClient, extractItemData, extractListData } from './client/httpClient';
import { RailmindApiError } from './client/errors';
import type { IMaintenanceService } from '../types';
import type { MaintenanceTask, Incident } from '../../domain';
import type { MaintenanceTaskListQuery, CreateMaintenanceTaskBody, DefectListQuery } from '../../contracts/api/maintenance';
import { mapDefectToIncident, mapMaintenanceTask } from './mappers';

function toPageParams(query?: { page?: number; pageSize?: number }): { page: number; page_size: number } {
  return { page: query?.page ?? 1, page_size: Math.min(query?.pageSize ?? 50, 100) };
}

export class ApiMaintenanceService implements IMaintenanceService {
  async getTasks(query?: MaintenanceTaskListQuery): Promise<MaintenanceTask[]> {
    // Backend supports only page/page_size today; richer filters are
    // intentionally not forwarded (documented contract gap).
    const env = await apiClient.get('/maintenance/tasks', { query: toPageParams(query) });
    return extractListData<unknown>(env, 'GET /maintenance/tasks').map(mapMaintenanceTask);
  }

  async getTaskById(id: string): Promise<MaintenanceTask | null> {
    const env = await apiClient.get(`/maintenance/tasks/${encodeURIComponent(id)}`);
    const item = extractItemData<unknown>(env, `GET /maintenance/tasks/${id}`);
    if (!item) return null;
    return mapMaintenanceTask(item);
  }

  async createTask(_body: CreateMaintenanceTaskBody): Promise<MaintenanceTask> {
    // POST /maintenance/tasks does not exist on the backend (documented gap).
    throw new RailmindApiError({
      kind: 'NOT_IMPLEMENTED',
      message: 'Task creation is not exposed by the backend yet (mock fallback in use).',
    });
  }

  async getDefects(query?: DefectListQuery): Promise<Incident[]> {
    const env = await apiClient.get('/maintenance/defects', { query: toPageParams(query) });
    return extractListData<unknown>(env, 'GET /maintenance/defects').map(mapDefectToIncident);
  }
}
