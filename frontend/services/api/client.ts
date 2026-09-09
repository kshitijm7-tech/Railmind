/**
 * RailMind Frontend API Client
 *
 * Centralized HTTP client for all FastAPI backend communication.
 * Provides consistent request/response mapping, error normalization,
 * and mock/real API switching capability.
 *
 * Architecture:
 *   UI
 *     ↓
 *   Feature Service Layer (uses this client)
 *     ↓
 *   HTTP Client (fetch wrapper with contract typing)
 *     ↓
 *   FastAPI Backend
 *
 * Key Design Decisions:
 * - Uses native fetch (no extra dependency)
 * - Base URL from environment variable (RAILMIND_API_BASE)
 * - Every request carries a correlationId for tracing
 * - Response normalized to ApiResponse<T> envelope
 * - ScenarioContext automatically attached to requests
 * - Mock mode supported via service layer interception
 */

import {
  ApiResponse,
  ApiListResponse,
  ApiMeta,
  RequestContext,
  ScenarioContext,
} from '../../contracts/api/common/envelope';
import {
  MaintenanceTaskListQuery,
  CreateMaintenanceTaskBody,
  DefectListQuery,
} from '../../contracts/api/maintenance/requests';
import {
  TrainListQuery,
} from '../../contracts/api/operations/requests';
import {
  PlanListQuery,
  GeneratePlanRequest,
  BlockListQuery,
  ComparePlansRequest,
} from '../../contracts/api/planning/requests';
import {
  RunSimulationRequest,
} from '../../contracts/api/simulation/requests';
import {
  DisruptionListQuery,
  CreateDisruptionBody,
} from '../../contracts/api/disruption/requests';
import {
  ApproveDecisionBody,
  RejectDecisionBody,
  DeferDecisionBody,
} from '../../contracts/api/decision/requests';
import {
  AuditEventListQuery,
} from '../../contracts/api/audit/requests';
import {
  AsyncJob,
} from '../../contracts/api/common/job';
import {
  DataState,
  DataSource,
  Provenance,
} from '../../contracts/common/provenance';
import {
  makeTimestamp,
  makeBlockId,
  makeTaskId,
  makePlanId,
  makeTrainId,
  makeScenarioId,
  makeDisruptionId,
  makeDecisionId,
  makeRecommendationId,
  makeWindowId,
} from '../../contracts/common/ids';

const defaultBaseUrl = typeof window !== 'undefined' ? '/' : (process.env.RAILMIND_API_BASE || 'http://localhost:8000');

let useMockMode = false;
let mockCorrelationIdCounter = 0;

/**
 * Switch between real API and mock mode.
 * Called by the service layer during initialization.
 */
export function setMockMode(enabled: boolean) {
  useMockMode = enabled;
}

/**
 * Get the current API base URL.
 */
export function getBaseUrl(): string {
  return defaultBaseUrl;
}

/**
 * Build headers for API requests.
 * Includes correlationId for request tracing and ScenarioContext when in scenario mode.
 */
function buildHeaders(
  scenarioContext?: ScenarioContext,
  extraHeaders: HeadersInit = {}
): HeadersInit {
  const correlationId = `RLM-${Date.now()}-${++mockCorrelationIdCounter}`;

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    'x-correlation-id': correlationId,
    ...extraHeaders,
  };

  return headers;
}

// ---- Request normalization ----

interface ClientSuccessResponse<T> {
  success: true;
  data: T;
  meta: ApiMeta;
}

interface ClientErrorResponse {
  success: false;
  meta: ApiMeta;
  error: {
    code: string;
    message: string;
    httpStatus: number;
  };
}

type ClientResponse<T> = ClientSuccessResponse<T> | ClientErrorResponse;

/**
 * Normalize a fetch response into the client response type.
 */
async function normalizeResponse<T>(
  response: Response
): Promise<ClientResponse<T>> {
  if (!response.ok) {
    const body = await response.json();
    const errorMessage = body.detail || 'Unknown server error';
    return {
      success: false,
      meta: {
        timestamp: makeTimestamp(new Date().toISOString()),
        requestId: response.headers.get('x-request-id') || '',
        apiVersion: 'v1',
      },
      error: {
        code: 'RAILMIND_099',
        message: errorMessage,
        httpStatus: response.status,
      },
    };
  }

  const data = (await response.json()) as T;
  return {
    success: true,
    data,
    meta: {
      timestamp: makeTimestamp(new Date().toISOString()),
      requestId: response.headers.get('x-request-id') || '',
      apiVersion: 'v1',
    },
  };
}

// ---- HTTP methods ----

export function get<T>(
  endpoint: string,
  params?: Record<string, string | number | boolean>,
  scenarioContext?: ScenarioContext
): Promise<{ success: boolean; data?: T; meta: ApiMeta; error?: { code: string; message: string; httpStatus: number } }> {
  return (async () => {
    const baseUrl = useMockMode ? '/' : getBaseUrl();
    const url = new URL(`${baseUrl}${endpoint}`);

    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          url.searchParams.append(key, String(value));
        }
      });
    }

    if (scenarioContext) {
      url.searchParams.append('scenarioContext', JSON.stringify(scenarioContext));
    }

    const headers = buildHeaders(scenarioContext);
    const response = await fetch(url.toString(), {
      method: 'GET',
      headers,
      credentials: 'include',
    });

    if (response.ok) {
      const data = (await response.json()) as T;
      return {
        success: true,
        data,
        meta: {
          timestamp: makeTimestamp(new Date().toISOString()),
          requestId: response.headers.get('x-request-id') || '',
          apiVersion: 'v1',
        },
      };
    }

    const errorBody = await response.json();
    return {
      success: false,
      meta: {
        timestamp: makeTimestamp(new Date().toISOString()),
        requestId: response.headers.get('x-request-id') || '',
        apiVersion: 'v1',
      },
      error: {
        code: errorBody.code || 'RAILMIND_099',
        message: errorBody.detail || 'Unknown server error',
        httpStatus: response.status,
      },
    };
  })();
}

export function post<T, B>(
  endpoint: string,
  body: B,
  scenarioContext?: ScenarioContext
): Promise<{ success: boolean; data?: T; meta: ApiMeta; error?: { code: string; message: string; httpStatus: number } }> {
  return (async () => {
    const baseUrl = useMockMode ? '/' : getBaseUrl();
    const url = new URL(`${baseUrl}${endpoint}`);

    if (scenarioContext) {
      url.searchParams.append('scenarioContext', JSON.stringify(scenarioContext));
    }

    const headers = buildHeaders(scenarioContext);
    const response = await fetch(url.toString(), {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
      credentials: 'include',
    });

    if (response.ok) {
      const data = (await response.json()) as T;
      return {
        success: true,
        data,
        meta: {
          timestamp: makeTimestamp(new Date().toISOString()),
          requestId: response.headers.get('x-request-id') || '',
          apiVersion: 'v1',
        },
      };
    }

    const errorBody = await response.json();
    return {
      success: false,
      meta: {
        timestamp: makeTimestamp(new Date().toISOString()),
        requestId: response.headers.get('x-request-id') || '',
        apiVersion: 'v1',
      },
      error: {
        code: errorBody.code || 'RAILMIND_099',
        message: errorBody.detail || 'Unknown server error',
        httpStatus: response.status,
      },
    };
  })();
};

export function put<T, B>(
  endpoint: string,
  body: B,
  scenarioContext?: ScenarioContext
): Promise<{ success: boolean; data?: T; meta: ApiMeta; error?: { code: string; message: string; httpStatus: number } }> {
  return (async () => {
    const baseUrl = useMockMode ? '/' : getBaseUrl();
    const url = new URL(`${baseUrl}${endpoint}`);

    if (scenarioContext) {
      url.searchParams.append('scenarioContext', JSON.stringify(scenarioContext));
    }

    const headers = buildHeaders(scenarioContext);
    const response = await fetch(url.toString(), {
      method: 'PUT',
      headers,
      body: JSON.stringify(body),
      credentials: 'include',
    });

    if (response.ok) {
      const data = (await response.json()) as T;
      return {
        success: true,
        data,
        meta: {
          timestamp: makeTimestamp(new Date().toISOString()),
          requestId: response.headers.get('x-request-id') || '',
          apiVersion: 'v1',
        },
      };
    }

    const errorBody = await response.json();
    return {
      success: false,
      meta: {
        timestamp: makeTimestamp(new Date().toISOString()),
        requestId: response.headers.get('x-request-id') || '',
        apiVersion: 'v1',
      },
      error: {
        code: errorBody.code || 'RAILMIND_099',
        message: errorBody.detail || 'Unknown server error',
        httpStatus: response.status,
      },
    };
  })();
};

export function del(
  endpoint: string,
  scenarioContext?: ScenarioContext
): Promise<{ success: boolean; data?: unknown; meta: ApiMeta; error?: { code: string; message: string; httpStatus: number } }> {
  return (async () => {
    const baseUrl = useMockMode ? '/' : getBaseUrl();
    const url = new URL(`${baseUrl}${endpoint}`);

    if (scenarioContext) {
      url.searchParams.append('scenarioContext', JSON.stringify(scenarioContext));
    }

    const headers = buildHeaders(scenarioContext);
    const response = await fetch(url.toString(), {
      method: 'DELETE',
      headers,
      credentials: 'include',
    });

    if (response.ok) {
      return {
        success: true,
        meta: {
          timestamp: makeTimestamp(new Date().toISOString()),
          requestId: response.headers.get('x-request-id') || '',
          apiVersion: 'v1',
        },
      };
    }

    const errorBody = await response.json();
    return {
      success: false,
      meta: {
        timestamp: makeTimestamp(new Date().toISOString()),
        requestId: response.headers.get('x-request-id') || '',
        apiVersion: 'v1',
      },
      error: {
        code: errorBody.code || 'RAILMIND_099',
        message: errorBody.detail || 'Unknown server error',
        httpStatus: response.status,
      },
    };
  })();
}

/**
 * Check if the frontend is currently in mock mode.
 */
export function isMockMode(): boolean {
  return useMockMode;
}

/**
 * Generate a mock correlationId for development when mock mode is active.
 */
export function generateMockCorrelationId(): string {
  return `MOCK-RLM-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

/**
 * Attach provenance information to a request.
 */
export function withProvenance(
  source: DataSource,
  state: DataState,
  actor?: string,
): Provenance {
  return {
    source,
    state,
    recordedAt: makeTimestamp(new Date().toISOString()),
    ...(actor && { actor }),
  };
}

export type { ApiResponse, ApiListResponse, ApiMeta, RequestContext, ScenarioContext };

export default {
  get,
  post,
  put,
  delete: del,
  isMockMode,
  setMockMode,
  getBaseUrl,
  generateMockCorrelationId,
};