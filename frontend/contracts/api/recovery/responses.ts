import { RecoveryPlan, RecoveryCandidate } from '../../disruption/recovery';
import { ApiResponse, ApiListResponse } from '../common/envelope';
import { JobAcceptedResponse } from '../common/job';

export type RecoveryPlanResponse = ApiResponse<RecoveryPlan>;
export type RecoveryCandidateListResponse = ApiListResponse<RecoveryCandidate>;
export type RecoveryReplanJobResponse = JobAcceptedResponse;
