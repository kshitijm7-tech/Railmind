import { Disruption } from '../../disruption/disruption';
import { TrainImpact } from '../../operations/train-impact';
import { ApiResponse, ApiListResponse } from '../common/envelope';

export type DisruptionResponse = ApiResponse<Disruption>;
export type DisruptionListResponse = ApiListResponse<Disruption>;

export interface ImpactAnalysisResult {
  readonly affectedTrains: TrainImpact[];
  readonly affectedBlockIds: string[];
  readonly totalDelayMinutes: number;
  readonly planInvalidated: boolean;
  readonly severity: string;
}
export type ImpactAnalysisResponse = ApiResponse<ImpactAnalysisResult>;
