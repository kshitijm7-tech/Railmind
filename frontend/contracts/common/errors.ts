import { ISOTimestamp } from './ids';

export type ErrorCategory = 'VALIDATION' | 'DOMAIN' | 'SYSTEM' | 'INTEGRATION' | 'AUTHORIZATION';
export type ErrorSeverity = 'INFO' | 'WARNING' | 'ERROR' | 'FATAL';

export interface DomainError {
  readonly code: string;
  readonly message: string;
  readonly category: ErrorCategory;
  readonly severity: ErrorSeverity;
  readonly field?: string;
  readonly details?: Record<string, unknown>;
  readonly correlationId?: string;
  readonly timestamp: ISOTimestamp;
}

// Stable machine-readable error codes
export const ERROR_CODES = {
  INVALID_TIME_INTERVAL: 'RAILMIND_001',
  INVALID_DURATION: 'RAILMIND_002',
  MISSING_REQUIRED_ID: 'RAILMIND_003',
  INVALID_LIFECYCLE_STATE: 'RAILMIND_004',
  INVALID_ENUM_VALUE: 'RAILMIND_005',
  CONFLICTING_BLOCK: 'RAILMIND_010',
  CONSTRAINT_VIOLATED: 'RAILMIND_011',
  PLAN_INVALIDATED: 'RAILMIND_020',
} as const;

export type ErrorCode = typeof ERROR_CODES[keyof typeof ERROR_CODES];
