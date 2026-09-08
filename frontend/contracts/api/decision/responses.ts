import { Recommendation } from '../../decision/recommendation';
import { Decision } from '../../decision/decision';
import { ApiResponse, ApiListResponse } from '../common/envelope';

export type RecommendationResponse = ApiResponse<Recommendation>;
export type RecommendationListResponse = ApiListResponse<Recommendation>;
export type DecisionResponse = ApiResponse<Decision>;
export type DecisionListResponse = ApiListResponse<Decision>;
