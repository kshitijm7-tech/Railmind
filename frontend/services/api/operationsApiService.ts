/** F01 — Real operations (train) API service (FastAPI). */
import { apiClient, extractItemData, extractListData } from './client/httpClient';
import type { ITrainService } from '../types';
import type { TrainService as DomainTrainService } from '../../domain';
import type { TrainListQuery } from '../../contracts/api/operations';
import { mapTrain } from './mappers';

export class ApiTrainService implements ITrainService {
  async getTrains(query?: TrainListQuery): Promise<DomainTrainService[]> {
    const env = await apiClient.get('/trains', {
      query: { page: query?.page ?? 1, page_size: Math.min(query?.pageSize ?? 50, 100) },
    });
    return extractListData<unknown>(env, 'GET /trains').map(mapTrain);
  }

  async getTrainById(id: string): Promise<DomainTrainService | null> {
    const env = await apiClient.get(`/trains/${encodeURIComponent(id)}`);
    const item = extractItemData<unknown>(env, `GET /trains/${id}`);
    if (!item) return null;
    return mapTrain(item);
  }
}
