import { describe, it, expect, vi, afterEach } from 'vitest';
import { apiClient } from '../services/api/client/httpClient';
import { RailmindApiError } from '../services/api/client/errors';

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('API client', () => {
  it('performs a successful GET and returns parsed JSON', async () => {
    const fetchMock = vi.fn(async () => jsonResponse({ data: 'OK' }));
    vi.stubGlobal('fetch', fetchMock);
    const result = await apiClient.get<{ data: string }>('/health');
    expect(result.data).toBe('OK');
    expect(fetchMock).toHaveBeenCalledOnce();
  });

  it('performs a successful POST with JSON body', async () => {
    const fetchMock = vi.fn(async (_url: unknown, init?: RequestInit) => {
      expect(init?.method).toBe('POST');
      expect(init?.headers).toMatchObject({ 'Content-Type': 'application/json' });
      return jsonResponse({ jobId: 'JOB-1', status: 'COMPLETED' }, 202);
    });
    vi.stubGlobal('fetch', fetchMock);
    const result = await apiClient.post<{ jobId: string }>('/planning/generate', { corridorId: 'CORR-A' });
    expect(result.jobId).toBe('JOB-1');
  });

  it('maps HTTP 404 to NOT_FOUND with backend message', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => jsonResponse({ detail: 'Task not found' }, 404)));
    try {
      await apiClient.get('/maintenance/tasks/MISSING');
      expect.unreachable();
    } catch (error: unknown) {
      expect(error).toBeInstanceOf(RailmindApiError);
      const err = error as RailmindApiError;
      expect(err.kind).toBe('NOT_FOUND');
      expect(err.httpStatus).toBe(404);
      expect(err.retryable).toBe(false);
    }
  });

  it('maps HTTP 500 to SERVER and marks retryable', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => jsonResponse({ error: { code: 'E', message: 'boom' } }, 500)));
    try {
      await apiClient.get('/plans');
      expect.unreachable();
    } catch (error: unknown) {
      const err = error as RailmindApiError;
      expect(err.kind).toBe('SERVER');
      expect(err.retryable).toBe(true);
    }
  });

  it('maps fetch rejection to NETWORK', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => {
      throw new TypeError('fetch failed');
    }));
    try {
      await apiClient.get('/trains');
      expect.unreachable();
    } catch (error: unknown) {
      expect((error as RailmindApiError).kind).toBe('NETWORK');
    }
  });

  it('maps malformed JSON to MALFORMED', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response('not-json{{{', { status: 200 })));
    try {
      await apiClient.get('/plans');
      expect.unreachable();
    } catch (error: unknown) {
      expect((error as RailmindApiError).kind).toBe('MALFORMED');
    }
  });

  it('aborts on caller signal with ABORTED', async () => {
    const controller = new AbortController();
    vi.stubGlobal(
      'fetch',
      vi.fn(async (_url: unknown, init?: { signal?: AbortSignal }) => {
        return new Promise((_resolve, reject) => {
          init?.signal?.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')));
        });
      }),
    );
    const pending = apiClient.get('/trains', { signal: controller.signal });
    controller.abort();
    try {
      await pending;
      expect.unreachable();
    } catch (error: unknown) {
      expect((error as RailmindApiError).kind).toBe('ABORTED');
    }
  });
});
