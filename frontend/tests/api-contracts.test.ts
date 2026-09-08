import { describe, it, expect } from 'vitest';
import { isJobComplete, JOB_TERMINAL_STATES } from '../contracts/api/common/job';
import { domainErrorToHttpStatus, toApiError, HTTP_STATUS } from '../contracts/api/common/errors';
import { API_ENDPOINTS } from '../contracts/api/endpoints';
import { makeTimestamp } from '../contracts/common/ids';
import type { PaginationMeta, ScenarioContext, ApiResponse, ApiMeta } from '../contracts/api/common/envelope';
import type { AsyncJob } from '../contracts/api/common/job';
import type { DomainError } from '../contracts/common/errors';
import type { GeneratePlanRequest } from '../contracts/api/planning';
import type { RunSimulationRequest } from '../contracts/api/simulation';

const mockTimestamp = makeTimestamp('2026-09-08T10:00:00Z');
const mockMeta: ApiMeta = { requestId: 'req-001', timestamp: mockTimestamp, apiVersion: 'v1' };

describe('AsyncJob lifecycle', () => {
  it('identifies terminal states correctly', () => {
    expect(isJobComplete('COMPLETED')).toBe(true);
    expect(isJobComplete('FAILED')).toBe(true);
    expect(isJobComplete('CANCELLED')).toBe(true);
    expect(isJobComplete('RUNNING')).toBe(false);
    expect(isJobComplete('QUEUED')).toBe(false);
  });

  it('AsyncJob shape is valid when complete', () => {
    const job: AsyncJob = {
      jobId: 'job-001',
      status: 'COMPLETED',
      requestedAt: mockTimestamp,
      completedAt: mockTimestamp,
      resultEndpoint: '/api/v1/plans/PLAN-001',
    };
    expect(job.status).toBe('COMPLETED');
    expect(job.resultEndpoint).toBeDefined();
  });

  it('AsyncJob shape is valid when failed', () => {
    const job: AsyncJob = {
      jobId: 'job-002',
      status: 'FAILED',
      requestedAt: mockTimestamp,
      errorCode: 'RAILMIND_020',
      errorMessage: 'Plan generation failed: no feasible solution',
    };
    expect(job.errorCode).toBe('RAILMIND_020');
  });
});

describe('API error mapping', () => {
  const baseDomainError: DomainError = {
    code: 'RAILMIND_001',
    message: 'Invalid interval',
    category: 'VALIDATION',
    severity: 'ERROR',
    timestamp: mockTimestamp,
  };

  it('maps VALIDATION category to 400', () => {
    expect(domainErrorToHttpStatus(baseDomainError)).toBe(HTTP_STATUS.BAD_REQUEST);
  });

  it('maps DOMAIN category to 422', () => {
    const err: DomainError = { ...baseDomainError, category: 'DOMAIN' };
    expect(domainErrorToHttpStatus(err)).toBe(HTTP_STATUS.UNPROCESSABLE);
  });

  it('maps AUTHORIZATION to 403', () => {
    const err: DomainError = { ...baseDomainError, category: 'AUTHORIZATION' };
    expect(domainErrorToHttpStatus(err)).toBe(HTTP_STATUS.FORBIDDEN);
  });

  it('maps SYSTEM to 500', () => {
    const err: DomainError = { ...baseDomainError, category: 'SYSTEM' };
    expect(domainErrorToHttpStatus(err)).toBe(HTTP_STATUS.INTERNAL_ERROR);
  });

  it('toApiError preserves code and message', () => {
    const apiErr = toApiError(baseDomainError);
    expect(apiErr.code).toBe('RAILMIND_001');
    expect(apiErr.message).toBe('Invalid interval');
    expect(apiErr.httpStatus).toBe(HTTP_STATUS.BAD_REQUEST);
  });
});

describe('ScenarioContext safety boundary', () => {
  it('LIVE mode does not require scenarioId', () => {
    const ctx: ScenarioContext = { mode: 'LIVE' };
    expect(ctx.mode).toBe('LIVE');
    expect(ctx.scenarioId).toBeUndefined();
  });

  it('SCENARIO mode carries scenarioId', () => {
    const ctx: ScenarioContext = { mode: 'SCENARIO', scenarioId: 'SCN-001' as unknown as import('../contracts/common/ids').ScenarioId };
    expect(ctx.mode).toBe('SCENARIO');
    expect(ctx.scenarioId).toBeDefined();
  });
});

describe('PaginationMeta contract', () => {
  it('first page with more data', () => {
    const p: PaginationMeta = { page: 1, pageSize: 20, total: 50, hasNext: true, hasPrev: false };
    expect(p.hasNext).toBe(true);
    expect(p.hasPrev).toBe(false);
  });

  it('last page', () => {
    const p: PaginationMeta = { page: 3, pageSize: 20, total: 50, hasNext: false, hasPrev: true };
    expect(p.hasNext).toBe(false);
  });
});

describe('API endpoints completeness', () => {
  it('covers all major domain areas', () => {
    const keys = Object.keys(API_ENDPOINTS);
    // Infrastructure
    expect(keys).toContain('ASSETS_LIST');
    expect(keys).toContain('TRACK_SECTIONS_LIST');
    // Maintenance
    expect(keys).toContain('TASKS_LIST');
    expect(keys).toContain('DEFECTS_LIST');
    // Operations
    expect(keys).toContain('TRAINS_LIST');
    expect(keys).toContain('OPERATIONAL_WINDOWS');
    // Planning
    expect(keys).toContain('PLAN_GENERATE');
    expect(keys).toContain('PLANS_COMPARE');
    // Simulation
    expect(keys).toContain('SIMULATION_RUN');
    // Disruption / Recovery
    expect(keys).toContain('DISRUPTIONS_LIST');
    expect(keys).toContain('RECOVERY_REPLAN');
    // Decision
    expect(keys).toContain('DECISION_APPROVE');
    expect(keys).toContain('DECISION_REJECT');
    // Audit / System
    expect(keys).toContain('AUDIT_EVENTS_LIST');
    expect(keys).toContain('HEALTH');
    expect(keys).toContain('JOB_STATUS');
  });

  it('all endpoints have method and path', () => {
    for (const [, endpoint] of Object.entries(API_ENDPOINTS)) {
      expect(endpoint.method).toBeTruthy();
      expect(endpoint.path).toMatch(/^\//);
    }
  });
});

describe('ApiResponse<T> envelope shape', () => {
  it('wraps data and includes meta', () => {
    const resp: ApiResponse<{ value: number }> = {
      data: { value: 42 },
      meta: mockMeta,
    };
    expect(resp.data.value).toBe(42);
    expect(resp.meta.apiVersion).toBe('v1');
    expect(resp.meta.requestId).toBe('req-001');
  });
});

describe('GeneratePlanRequest contract alignment', () => {
  it('requires horizon, corridorId, and strategy', () => {
    const req: GeneratePlanRequest = {
      horizon: {
        start: makeTimestamp('2026-09-08T02:00:00Z'),
        end: makeTimestamp('2026-09-11T02:00:00Z'),
      },
      corridorId: 'CORR-07' as unknown as import('../contracts/common/ids').CorridorId,
      strategy: 'BALANCED',
    };
    expect(req.strategy).toBe('BALANCED');
    expect(req.scenarioContext).toBeUndefined();
  });
});

describe('RunSimulationRequest requires scenarioContext', () => {
  it('scenarioContext is required on simulation request', () => {
    const req: RunSimulationRequest = {
      planId: 'PLAN-001' as unknown as import('../contracts/common/ids').PlanId,
      scenarioId: 'SCN-001' as unknown as import('../contracts/common/ids').ScenarioId,
      scenarioContext: { mode: 'SCENARIO', scenarioId: 'SCN-001' as unknown as import('../contracts/common/ids').ScenarioId },
    };
    expect(req.scenarioContext.mode).toBe('SCENARIO');
  });
});
