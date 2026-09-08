import { Block, CandidateBlockWindow } from '../../planning/block';
import { Plan, PlanVersion } from '../../planning/plan';
import { PlanMetrics } from '../../planning/plan-metrics';
import { TrainImpact } from '../../operations/train-impact';
import { ApiResponse, ApiListResponse } from '../common/envelope';
import { JobAcceptedResponse } from '../common/job';

export type BlockResponse = ApiResponse<Block>;
export type BlockListResponse = ApiListResponse<Block>;
export type CandidateWindowListResponse = ApiListResponse<CandidateBlockWindow>;

export type PlanResponse = ApiResponse<Plan>;
export type PlanListResponse = ApiListResponse<Plan>;
export type PlanVersionsResponse = ApiListResponse<PlanVersion>;
export type PlanMetricsResponse = ApiResponse<PlanMetrics>;
export type PlanImpactsResponse = ApiListResponse<TrainImpact>;

// POST /planning/generate -> 202 Accepted
export type PlanGenerationJobResponse = JobAcceptedResponse;

export interface PlanComparisonEntry {
  readonly planId: string;
  readonly planName: string;
  readonly strategy: string;
  readonly metrics: PlanMetrics;
  readonly trainImpactCount: number;
  readonly constraintViolations: number;
  readonly overrunRisk: number;
  readonly recommendationRank: number;
}

export interface ComparePlansResponse {
  readonly candidates: PlanComparisonEntry[];
  readonly recommendedPlanId: string;
  readonly tradeoffSummary: string[];
}
