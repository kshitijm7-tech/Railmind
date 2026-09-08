import { SimulationRun } from '../../simulation/simulation-run';
import { SimulationResult } from '../../simulation/simulation-result';
import { ApiResponse, ApiListResponse } from '../common/envelope';
import { JobAcceptedResponse } from '../common/job';

export type SimulationJobResponse = JobAcceptedResponse;
export type SimulationRunResponse = ApiResponse<SimulationRun>;
export type SimulationRunListResponse = ApiListResponse<SimulationRun>;
export type SimulationResultResponse = ApiResponse<SimulationResult>;
