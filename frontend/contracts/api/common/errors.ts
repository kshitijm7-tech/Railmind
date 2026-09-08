import { ISOTimestamp } from '../../common/ids';
import { DomainError } from '../../common/errors';

// HTTP status codes used by the RailMind API
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  ACCEPTED: 202,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,   // auth placeholder
  FORBIDDEN: 403,      // authz placeholder
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE: 422,
  TOO_MANY_REQUESTS: 429, // rate-limit placeholder
  INTERNAL_ERROR: 500,
  SERVICE_UNAVAILABLE: 503,
} as const;

export type HttpStatus = typeof HTTP_STATUS[keyof typeof HTTP_STATUS];

// API-level error (safe to expose to consumers — no stack traces)
export interface ApiError {
  readonly httpStatus: HttpStatus;
  readonly code: string;          // stable machine-readable code from ERROR_CODES
  readonly message: string;       // human-readable summary
  readonly field?: string;        // which field failed validation (if applicable)
  readonly details?: Record<string, unknown>;
  readonly correlationId?: string;
  readonly timestamp: ISOTimestamp;
}

// Standard error response envelope
export interface ApiErrorResponse {
  readonly error: ApiError;
}

// Map DomainError category to HTTP status
export function domainErrorToHttpStatus(err: DomainError): HttpStatus {
  switch (err.category) {
    case 'VALIDATION':    return HTTP_STATUS.BAD_REQUEST;
    case 'DOMAIN':        return HTTP_STATUS.UNPROCESSABLE;
    case 'AUTHORIZATION': return HTTP_STATUS.FORBIDDEN;
    case 'INTEGRATION':   return HTTP_STATUS.SERVICE_UNAVAILABLE;
    case 'SYSTEM':        return HTTP_STATUS.INTERNAL_ERROR;
    default:              return HTTP_STATUS.INTERNAL_ERROR;
  }
}

// Build a safe API error from a domain error
export function toApiError(err: DomainError, httpStatus?: HttpStatus): ApiError {
  return {
    httpStatus: httpStatus ?? domainErrorToHttpStatus(err),
    code: err.code,
    message: err.message,
    field: err.field,
    details: err.details,
    correlationId: err.correlationId,
    timestamp: err.timestamp,
  };
}
