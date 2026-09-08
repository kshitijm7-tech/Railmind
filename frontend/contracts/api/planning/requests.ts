import { PlanId, BlockId, SectionId, CorridorId, ScenarioId, ISOTimestamp } from '../../common/ids';
import { PaginationParams, SortParams, ScenarioContext } from '../common/envelope';
import { BlockStatus } from '../../planning/block';
import { PlanStatus, PlanStrategy } from '../../planning/plan';
import { TimeInterval } from '../../common/time';

export interface BlockListQuery extends PaginationParams, SortParams {
  readonly sectionId?: SectionId;
  readonly status?: BlockStatus;
  readonly from?: ISOTimestamp;
  readonly to?: ISOTimestamp;
  readonly scenarioContext?: ScenarioContext;
}

export interface BlockRequestBody {
  readonly sectionId: SectionId;
  readonly requestedInterval: TimeInterval;
  readonly purpose: string;
  readonly taskIds: string[];
  readonly requiresPowerOff: boolean;
  readonly scenarioContext?: ScenarioContext;
}

export interface GeneratePlanRequest {
  readonly horizon: TimeInterval;
  readonly corridorId: CorridorId;
  readonly strategy: PlanStrategy;
  readonly taskIds?: string[];         // specific tasks to schedule, or all pending
  readonly objectiveWeights?: Record<string, number>;
  readonly scenarioContext?: ScenarioContext; // LIVE or SCENARIO — safety boundary
  readonly idempotencyKey?: string;    // prevent duplicate plan generation
}

export interface PlanListQuery extends PaginationParams, SortParams {
  readonly status?: PlanStatus;
  readonly corridorId?: CorridorId;
  readonly scenarioContext?: ScenarioContext;
}

export interface ComparePlansRequest {
  readonly planIds: PlanId[]; // 2-5 plans to compare
  readonly scenarioContext?: ScenarioContext;
}
