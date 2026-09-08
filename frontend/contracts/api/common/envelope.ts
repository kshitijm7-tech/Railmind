import { ISOTimestamp } from '../../common/ids';
import { StateMode } from '../../common/enums';
import { ScenarioId } from '../../common/ids';

export const API_VERSION = 'v1' as const;
export const API_BASE = '/api/v1' as const;

// Request tracing — every request carries this
export interface RequestContext {
  readonly requestId: string;
  readonly correlationId?: string;
  readonly timestamp: ISOTimestamp;
  readonly actor?: string; // placeholder for future auth
  readonly scenarioContext?: ScenarioContext;
}

// SAFETY BOUNDARY: SCENARIO mode must never silently mutate LIVE state
export interface ScenarioContext {
  readonly mode: StateMode;
  readonly scenarioId?: ScenarioId; // required when mode === 'SCENARIO'
}

// Standard response metadata
export interface ApiMeta {
  readonly requestId: string;
  readonly timestamp: ISOTimestamp;
  readonly apiVersion: typeof API_VERSION;
  readonly correlationId?: string;
}

// Standard single-item response
export interface ApiResponse<T> {
  readonly data: T;
  readonly meta: ApiMeta;
}

// Pagination metadata
export interface PaginationMeta {
  readonly page: number;
  readonly pageSize: number;
  readonly total: number;
  readonly hasNext: boolean;
  readonly hasPrev: boolean;
}

// Standard list response
export interface ApiListResponse<T> {
  readonly data: T[];
  readonly meta: ApiMeta;
  readonly pagination: PaginationMeta;
}

// Pagination query params
export interface PaginationParams {
  readonly page?: number;       // default: 1
  readonly pageSize?: number;   // default: 20, max: 100
}

// Sorting query params
export interface SortParams {
  readonly sortBy?: string;
  readonly sortDirection?: 'asc' | 'desc'; // default: 'asc'
}

// Common date range filter
export interface DateRangeFilter {
  readonly from?: ISOTimestamp;
  readonly to?: ISOTimestamp;
}

// Idempotency support for state-changing commands
export interface IdempotencyHeader {
  readonly idempotencyKey: string; // UUID, client-generated
}
