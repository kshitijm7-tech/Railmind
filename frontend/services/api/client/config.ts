/**
 * F01 — API environment configuration.
 *
 * Single source of truth for backend connectivity. No service or component
 * should hard-code a base URL.
 *
 * Conventions:
 * - NEXT_PUBLIC_API_BASE_URL: backend origin, e.g. http://localhost:8000
 * - NEXT_PUBLIC_API_MODE: "auto" | "real" | "mock" (default "auto")
 * - NEXT_PUBLIC_API_TIMEOUT_MS: request timeout (default 10000)
 * - NEXT_PUBLIC_API_DEBUG: "true" enables dev-only request diagnostics
 */

export type ApiModeSetting = 'auto' | 'real' | 'mock';

export type ResolvedApiMode = 'real' | 'mock';

const DEFAULT_BASE_URL = 'http://localhost:8000';
const DEFAULT_TIMEOUT_MS = 10_000;

function readEnv(name: string): string | undefined {
  if (typeof process === 'undefined') return undefined;
  const env = (process as { env?: Record<string, string | undefined> }).env;
  return env?.[name];
}

export function getApiBaseUrl(): string {
  const raw = readEnv('NEXT_PUBLIC_API_BASE_URL')?.trim();
  if (!raw) return DEFAULT_BASE_URL;
  // Strip trailing slashes so path joining is predictable.
  return raw.replace(/\/+$/, '');
}

export function getApiModeSetting(): ApiModeSetting {
  const raw = readEnv('NEXT_PUBLIC_API_MODE')?.trim().toLowerCase();
  if (raw === 'real' || raw === 'mock' || raw === 'auto') return raw;
  return 'auto';
}

export function getApiTimeoutMs(): number {
  const raw = readEnv('NEXT_PUBLIC_API_TIMEOUT_MS');
  const parsed = raw ? Number.parseInt(raw, 10) : NaN;
  if (Number.isFinite(parsed) && parsed > 0) return parsed;
  return DEFAULT_TIMEOUT_MS;
}

export function isApiDebugEnabled(): boolean {
  return readEnv('NEXT_PUBLIC_API_DEBUG')?.toLowerCase() === 'true';
}

/**
 * Backend API path prefix. Backend serves FastAPI under /api/v1 and
 * /health at the root. Frontend dev server proxies /api/v1 to the backend
 * (see next.config.ts) so browser traffic stays same-origin and avoids CORS.
 */
export const API_PATH_PREFIX = '/api/v1';

export function buildApiUrl(path: string): string {
  if (!path.startsWith('/')) return `${getApiBaseUrl()}${API_PATH_PREFIX}/${path}`;
  if (path.startsWith(API_PATH_PREFIX) || path === '/health') {
    // Absolute backend path — prefix with origin when running server-side.
    // In the browser, same-origin relative URLs use the Next rewrite proxy.
    if (typeof window === 'undefined') return `${getApiBaseUrl()}${path}`;
    return path;
  }
  if (typeof window === 'undefined') return `${getApiBaseUrl()}${API_PATH_PREFIX}${path}`;
  return `${API_PATH_PREFIX}${path}`;
}

/**
 * Resolve the effective mode. "auto" prefers real and falls back to mock
 * only when the backend is unreachable (network/timeout/server errors on
 * safe idempotent reads). Explicit "real"/"mock" never falls back silently —
 * callers surface the error instead.
 */
export function resolveServiceMode(setting: ApiModeSetting, backendReachable: boolean): ResolvedApiMode {
  if (setting === 'real') return 'real';
  if (setting === 'mock') return 'mock';
  return backendReachable ? 'real' : 'mock';
}
