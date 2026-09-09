/** F01 — Real infrastructure API service (FastAPI). */
import { apiClient, extractItemData, extractListData } from './client/httpClient';
import { RailmindApiError } from './client/errors';
import type { INetworkService } from '../types';
import type { RailwayNetwork, RailwayStateMetadata } from '../../domain';
import { mapNetwork } from './mappers';

export class ApiInfrastructureService implements INetworkService {
  async getNetwork(): Promise<RailwayNetwork> {
    const [assetsEnv, sectionsEnv, corridorsEnv] = await Promise.all([
      apiClient.get('/assets', { query: { page: 1, page_size: 100 } }),
      apiClient.get('/track-sections', { query: { page: 1, page_size: 100 } }),
      apiClient.get('/corridors', { query: { page: 1, page_size: 100 } }),
    ]);
    const assets = extractListData<unknown>(assetsEnv, 'GET /assets');
    const sections = extractListData<unknown>(sectionsEnv, 'GET /track-sections');
    const corridors = extractListData<unknown>(corridorsEnv, 'GET /corridors');
    return mapNetwork(assets, sections, corridors);
  }

  async getAssetById(assetId: string): Promise<unknown> {
    const env = await apiClient.get(`/assets/${encodeURIComponent(assetId)}`);
    const item = extractItemData<unknown>(env, `GET /assets/${assetId}`);
    if (!item) {
      throw new RailmindApiError({ kind: 'NOT_FOUND', message: `Asset ${assetId} was not found.` });
    }
    return item;
  }

  async getStateMetadata(): Promise<RailwayStateMetadata> {
    // No backend endpoint exposes operational state metadata (documented gap).
    throw new RailmindApiError({
      kind: 'NOT_IMPLEMENTED',
      message: 'State metadata is not exposed by the backend yet (mock fallback in use).',
    });
  }
}
