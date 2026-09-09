/**
 * F01 — Centralized HTTP/API client.
 *
 * All frontend -> FastAPI traffic goes through this module:
 *   Component -> Service -> ApiClient (here) -> FastAPI
 *
 * No component should call fetch() directly for domain APIs.
 */

import { buildApiUrl, getApiTimeoutMs, isApiDebugEnabled } from './config';
import { RailmindApiError, httpStatusToKind } from './errors';

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export interface RequestOptions {
  method?: HttpMethod;
  query?: Record<string, string | number | boolean | undefined | null>;
  body?: unknown;
  signal?: AbortSignal;
  timeoutMs?: number;
  /** Forwarded as X-Idempotency-Key for state-changing commands. */
  idempotencyKey?: string;
  headers?: Record<string, string>;
}

interface BackendErrorPayload {
  error?: { code?: string; message?: string; httpStatus?: number };
  detail?: string;
}

function newRequestId(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) return crypto.randomUUID();
  return `req-${Date.now()}-${Math.floor(Math.random() * 1e6)}`;
}

function buildQueryString(query?: RequestOptions['query']): string {
  if (!query) return '';
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value === undefined || value === null) continue;
    params.append(key, String(value));
  }
  const qs = params.toString();
  return qs ? `?${qs}` : '';
}

function debugLog(message: string, extra?: unknown): void {
  if (!isApiDebugEnabled()) return;
  // Dev-only diagnostics. Never log tokens/credentials (none are handled here).
  if (typeof console !== 'undefined') console.debug(`[RailMind API] ${message}`, extra ?? '');
}

function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === 'AbortError';
}

/**
 * Placeholder for future auth (F01: no auth contracts exist, do not invent).
 * Centralizes where Authorization headers will be attached.
 */
function getAuthToken(): string | undefined {
  return undefined;
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const method = options.method ?? 'GET';
  const timeoutMs = options.timeoutMs ?? getApiTimeoutMs();
  const url = `${buildApiUrl(path)}${buildQueryString(options.query)}`;

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(new DOMException('Timeout', 'AbortError')), timeoutMs);

  const onExternalAbort = (): void => {
    controller.abort(options.signal?.reason ?? new DOMException('Aborted', 'AbortError'));
  };
  if (options.signal) {
    if (options.signal.aborted) onExternalAbort();
    else options.signal.addEventListener('abort', onExternalAbort, { once: true });
  }

  const headers: Record<string, string> = { Accept: 'application/json', ...(options.headers ?? {}) };
  let body: string | undefined;
  if (options.body !== undefined) {
    headers['Content-Type'] = 'application/json';
    body = JSON.stringify(options.body);
  }
  headers['X-Request-ID'] = newRequestId();
  if (options.idempotencyKey) headers['X-Idempotency-Key'] = options.idempotencyKey;
  const token = getAuthToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  debugLog(`${method} ${url}`);

  let response: Response;
  try {
    response = await fetch(url, { method, headers, body, signal: controller.signal });
  } catch (error: unknown) {
    if (options.signal) options.signal.removeEventListener('abort', onExternalAbort);
    if (isAbortError(error)) {
      // Distinguish caller cancellation from our timeout.
      if (options.signal?.aborted) {
        throw new RailmindApiError({ kind: 'ABORTED', message: 'Request was cancelled.' });
      }
      throw new RailmindApiError({ kind: 'TIMEOUT', message: `Request timed out after ${timeoutMs}ms.` });
    }
    throw new RailmindApiError({
      kind: 'NETWORK',
      message: 'Network failure while reaching the backend.',
      details: { url: stripOrigin(url) },
    });
  } finally {
    clearTimeout(timeout);
    if (options.signal) options.signal.removeEventListener('abort', onExternalAbort);
  }

  if (response.status === 204) return undefined as T;

  let payload: unknown = undefined;
  const text = await response.text().catch(() => '');
  if (text) {
    try {
      payload = JSON.parse(text) as unknown;
    } catch {
      if (!response.ok) {
        throw new RailmindApiError({
          kind: httpStatusToKind(response.status),
          message: `Backend returned HTTP ${response.status} with a non-JSON body.`,
          httpStatus: response.status,
        });
      }
      throw new RailmindApiError({ kind: 'MALFORMED', message: 'Backend returned malformed JSON.' });
    }
  }

  if (!response.ok) {
    const backend = (payload ?? {}) as BackendErrorPayload;
    const message =
      backend.error?.message?.trim() ||
      (typeof backend.detail === 'string' && backend.detail.trim()) ||
      `Backend returned HTTP ${response.status}.`;
    throw new RailmindApiError({
      kind: httpStatusToKind(response.status),
      message,
      code: backend.error?.code ?? `HTTP_${response.status}`,
      httpStatus: response.status,
    });
  }

  return payload as T;
}

function stripOrigin(url: string): string {
  try {
    const parsed = new URL(url, 'http://local');
    return parsed.pathname + parsed.search;
  } catch {
    return url;
  }
}

export const apiClient = {
  get: <T>(path: string, options?: Omit<RequestOptions, 'method' | 'body'>) =>
    apiRequest<T>(path, { ...options, method: 'GET' }),
  post: <T>(path: string, body?: unknown, options?: Omit<RequestOptions, 'method' | 'body'>) =>
    apiRequest<T>(path, { ...options, method: 'POST', body }),
  put: <T>(path: string, body?: unknown, options?: Omit<RequestOptions, 'method' | 'body'>) =>
    apiRequest<T>(path, { ...options, method: 'PUT', body }),
  patch: <T>(path: string, body?: unknown, options?: Omit<RequestOptions, 'method' | 'body'>) =>
    apiRequest<T>(path, { ...options, method: 'PATCH', body }),
  delete: <T>(path: string, options?: Omit<RequestOptions, 'method' | 'body'>) =>
    apiRequest<T>(path, { ...options, method: 'DELETE' }),
};

/** Backend envelope helpers (snake_case wire format, tolerant to missing fields). */

export interface BackendListEnvelope<T> {
  data?: T[] | null;
  pagination?: { totalItems?: number; page?: number; pageSize?: number; totalPages?: number } | null;
  error?: { code?: string; message?: string; httpStatus?: number } | null;
}

export interface BackendItemEnvelope<T> {
  data?: T | null;
  error?: { code?: string; message?: string; httpStatus?: number } | null;
}

export function extractListData<T>(envelope: unknown, endpoint: string): T[] {
  if (envelope !== null && typeof envelope === 'object' && 'data' in envelope) {
    const data = (envelope as BackendListEnvelope<T>).data;
    if (data === undefined || data === null) return [];
    if (!Array.isArray(data)) {
      throw new RailmindApiError({ kind: 'MALFORMED', message: `Unexpected list shape from ${endpoint}.` });
    }
    return data;
  }
  if (Array.isArray(envelope)) return envelope as T[];
  throw new RailmindApiError({ kind: 'MALFORMED', message: `Unexpected list shape from ${endpoint}.` });
}

export function extractItemData<T>(envelope: unknown, endpoint: string): T | null {
  if (envelope !== null && typeof envelope === 'object' && 'data' in envelope) {
    const data = (envelope as BackendItemEnvelope<T>).data;
    if (data === undefined || data === null) return null;
    return data;
  }
  if (envelope === null || envelope === undefined) return null;
  return envelope as T;
}
