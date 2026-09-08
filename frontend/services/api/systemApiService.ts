/** F01 — Backend reachability / version probe (FastAPI). */
import { apiClient, extractItemData } from './client/httpClient';

export async function probeBackendReachability(signal?: AbortSignal): Promise<boolean> {
  try {
    await apiClient.get('/health', { signal, timeoutMs: 4000 });
    return true;
  } catch {
    return false;
  }
}

export async function fetchBackendVersion(signal?: AbortSignal): Promise<string | null> {
  try {
    const env = await apiClient.get('/version', { signal, timeoutMs: 4000 });
    const data = extractItemData<unknown>(env, 'GET /version');
    if (data !== null && typeof data === 'object' && 'version' in data) {
      const version = (data as { version?: unknown }).version;
      return typeof version === 'string' ? version : null;
    }
    return null;
  } catch {
    return null;
  }
}
