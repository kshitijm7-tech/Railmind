import { ISOTimestamp } from '../../common/ids';
import { ApiResponse } from '../common/envelope';

export type ServiceStatus = 'ok' | 'degraded' | 'unavailable';

export interface ServiceHealth {
  readonly name: string;
  readonly status: ServiceStatus;
  readonly latencyMs?: number;
}

export interface HealthData {
  readonly status: ServiceStatus;
  readonly version: string;
  readonly timestamp: ISOTimestamp;
  readonly services?: ServiceHealth[];
}

export type HealthResponse = ApiResponse<HealthData>;
export type ApiVersionResponse = ApiResponse<{ version: string; releaseDate: ISOTimestamp }>;
