/**
 * F01 — Normalized API error strategy.
 *
 * Flow: transport/HTTP/backend error -> RailmindApiError -> UI error state.
 * Raw stack traces and backend internals never reach the UI.
 */

export type ApiErrorKind =
  | 'NETWORK'
  | 'TIMEOUT'
  | 'ABORTED'
  | 'UNAUTHORIZED'
  | 'FORBIDDEN'
  | 'VALIDATION'
  | 'NOT_FOUND'
  | 'CONFLICT'
  | 'RATE_LIMITED'
  | 'SERVER'
  | 'MALFORMED'
  | 'NOT_IMPLEMENTED'
  | 'UNKNOWN';

export type ApiSource = 'REAL' | 'MOCK';

export class RailmindApiError extends Error {
  readonly kind: ApiErrorKind;
  readonly httpStatus?: number;
  readonly code: string;
  readonly field?: string;
  readonly details?: Record<string, unknown>;
  readonly correlationId?: string;
  readonly retryable: boolean;
  readonly source: ApiSource;

  constructor(args: {
    kind: ApiErrorKind;
    message: string;
    code?: string;
    httpStatus?: number;
    field?: string;
    details?: Record<string, unknown>;
    correlationId?: string;
    retryable?: boolean;
    source?: ApiSource;
  }) {
    super(args.message);
    this.name = 'RailmindApiError';
    this.kind = args.kind;
    this.code = args.code ?? `F01_${args.kind}`;
    this.httpStatus = args.httpStatus;
    this.field = args.field;
    this.details = args.details;
    this.correlationId = args.correlationId;
    this.retryable = args.retryable ?? defaultRetryable(args.kind);
    this.source = args.source ?? 'REAL';
  }
}

function defaultRetryable(kind: ApiErrorKind): boolean {
  switch (kind) {
    case 'NETWORK':
    case 'TIMEOUT':
    case 'SERVER':
    case 'RATE_LIMITED':
      return true;
    default:
      return false;
  }
}

export function httpStatusToKind(status: number): ApiErrorKind {
  if (status === 401) return 'UNAUTHORIZED';
  if (status === 403) return 'FORBIDDEN';
  if (status === 404) return 'NOT_FOUND';
  if (status === 409) return 'CONFLICT';
  if (status === 429) return 'RATE_LIMITED';
  if (status === 400 || status === 422) return 'VALIDATION';
  if (status >= 500) return 'SERVER';
  return 'UNKNOWN';
}

/** Safe, user-facing message. Never includes stack traces or tokens. */
export function toUserMessage(error: unknown): string {
  if (error instanceof RailmindApiError) {
    switch (error.kind) {
      case 'NETWORK':
        return 'Backend unreachable. Check that the FastAPI service is running or switch to mock mode.';
      case 'TIMEOUT':
        return 'Backend request timed out. Retry or narrow the query.';
      case 'ABORTED':
        return 'Request was cancelled.';
      case 'UNAUTHORIZED':
        return 'Session expired or missing credentials.';
      case 'FORBIDDEN':
        return 'Operation not permitted for this role.';
      case 'VALIDATION':
        return error.message || 'Request was rejected by validation.';
      case 'NOT_FOUND':
        return error.message || 'Requested record was not found.';
      case 'CONFLICT':
        return error.message || 'Request conflicts with current railway state.';
      case 'RATE_LIMITED':
        return 'Too many requests. Retry shortly.';
      case 'SERVER':
        return 'Backend reported an internal error. Live safety state is unchanged.';
      case 'MALFORMED':
        return 'Backend returned an unexpected response shape.';
      case 'NOT_IMPLEMENTED':
        return error.message || 'This capability is not available on the backend yet (mock fallback in use).';
      default:
        return error.message || 'An unexpected integration error occurred.';
    }
  }
  if (error instanceof Error) return 'An unexpected integration error occurred.';
  return 'An unexpected integration error occurred.';
}

/** Type guard for service-layer error propagation tests. */
export function isRailmindApiError(error: unknown): error is RailmindApiError {
  return error instanceof RailmindApiError;
}
