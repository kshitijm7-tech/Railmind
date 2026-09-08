import { describe, it, expect, vi, afterEach } from 'vitest';
import { ApiMaintenanceService } from '../services/api/maintenanceApiService';
import { ApiPlanningService } from '../services/api/planningApiService';
import { ApiTrainService } from '../services/api/operationsApiService';
import { createServices } from '../services/api/serviceFactory';
import { RailmindApiError } from '../services/api/client/errors';

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

function listEnvelope<T>(items: T[]): unknown {
  return {
    data: items,
    pagination: { totalItems: items.length, page: 1, pageSize: 50, totalPages: 1 },
    meta: { timestamp: new Date().toISOString(), requestId: 'req-1', version: 'v1.0.0' },
  };
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('API services', () => {
  it('builds page/page_size queries for task lists', async () => {
    let seenUrl = '';
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: unknown) => {
        seenUrl = String(url);
        return jsonResponse(listEnvelope([]));
      }),
    );
    await new ApiMaintenanceService().getTasks({ page: 2, pageSize: 25 });
    expect(seenUrl).toContain('/maintenance/tasks');
    expect(seenUrl).toContain('page=2');
    expect(seenUrl).toContain('page_size=25');
  });

  it('parses train list responses through the service layer', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () =>
        jsonResponse(
          listEnvelope([
            {
              service: {
                train_id: 'TRN-500',
                name: 'Rajdhani Express',
                train_number: '12951',
                type: 'EXPRESS',
                origin_station_id: 'ST-1',
                destination_station_id: 'ST-3',
                sections: [],
              },
              priority: 1,
            },
          ]),
        ),
      ),
    );
    const trains = await new ApiTrainService().getTrains();
    expect(trains).toHaveLength(1);
    expect(trains[0]?.train_id).toBe('TRN-500');
  });

  it('propagates typed errors for missing plans', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => jsonResponse({ detail: 'Not found' }, 404)));
    try {
      await new ApiPlanningService().getPlanById('MISSING');
      expect.unreachable();
    } catch (error: unknown) {
      expect(error).toBeInstanceOf(RailmindApiError);
      expect((error as RailmindApiError).kind).toBe('NOT_FOUND');
    }
  });

  it('returns async jobs for plan generation', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () =>
        jsonResponse({ jobId: 'JOB-1', status: 'COMPLETED', requestedAt: new Date().toISOString() }, 202),
      ),
    );
    const job = await new ApiPlanningService().generatePlan({
      horizon: {
        start: '2026-09-08T02:00:00Z' as unknown as import('../contracts/common/ids').ISOTimestamp,
        end: '2026-09-11T02:00:00Z' as unknown as import('../contracts/common/ids').ISOTimestamp,
      },
      corridorId: 'CORR-07' as unknown as import('../contracts/common/ids').CorridorId,
      strategy: 'BALANCED',
    });
    expect(job.jobId).toBe('JOB-1');
    expect(job.status).toBe('COMPLETED');
  });

  it('falls back to mock in auto mode when the backend is unreachable', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => {
        throw new TypeError('fetch failed');
      }),
    );
    const auto = createServices('auto');
    const tasks = await auto.maintenance.getTasks();
    expect(tasks.length).toBeGreaterThan(0);
  });

  it('does not fall back in real mode (errors propagate)', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => {
        throw new TypeError('fetch failed');
      }),
    );
    const real = createServices('real');
    try {
      await real.maintenance.getTasks();
      expect.unreachable();
    } catch (error: unknown) {
      expect((error as RailmindApiError).kind).toBe('NETWORK');
    }
  });

  it('mock and real containers satisfy the same service expectations', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => {
        throw new TypeError('fetch failed');
      }),
    );
    const mock = createServices('mock');
    const auto = createServices('auto');
    const mockTasks = await mock.maintenance.getTasks();
    const autoTasks = await auto.maintenance.getTasks();
    expect(Array.isArray(mockTasks)).toBe(true);
    expect(Array.isArray(autoTasks)).toBe(true);
    expect(mockTasks.length).toBe(autoTasks.length);
  });
});
