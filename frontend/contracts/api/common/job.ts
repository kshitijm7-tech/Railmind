import { ISOTimestamp } from '../../common/ids';

export type JobStatus = 'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';

// Generic async job — returned as 202 Accepted for long-running operations
// e.g. plan generation, simulation, recovery optimization
export interface AsyncJob {
  readonly jobId: string;
  readonly status: JobStatus;
  readonly requestedAt: ISOTimestamp;
  readonly startedAt?: ISOTimestamp;
  readonly completedAt?: ISOTimestamp;
  readonly progressPercent?: number; // 0-100 if available
  readonly resultEndpoint?: string;  // poll URL when COMPLETED
  readonly errorCode?: string;       // stable code when FAILED
  readonly errorMessage?: string;
}

// Accepted response when a long-running job is enqueued
export interface JobAcceptedResponse {
  readonly jobId: string;
  readonly status: 'QUEUED';
  readonly pollEndpoint: string; // e.g. /api/v1/jobs/{jobId}
  readonly estimatedDurationSeconds?: number;
}

// Valid job status transitions
// QUEUED -> RUNNING -> COMPLETED
// QUEUED -> RUNNING -> FAILED
// QUEUED -> CANCELLED
// RUNNING -> CANCELLED
export const JOB_TERMINAL_STATES: JobStatus[] = ['COMPLETED', 'FAILED', 'CANCELLED'];
export function isJobComplete(status: JobStatus): boolean {
  return JOB_TERMINAL_STATES.includes(status);
}
