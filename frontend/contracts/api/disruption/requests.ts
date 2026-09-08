import { DisruptionId, PlanId, SectionId } from '../../common/ids';
import { Criticality } from '../../common/enums';
import { PaginationParams, SortParams, DateRangeFilter, ScenarioContext } from '../common/envelope';
import { DisruptionType, IncidentStatus } from '../../disruption/disruption';
import { TimeInterval } from '../../common/time';

export interface DisruptionListQuery extends PaginationParams, SortParams, DateRangeFilter {
  readonly type?: DisruptionType;
  readonly status?: IncidentStatus;
  readonly sectionId?: SectionId;
  readonly criticality?: Criticality;
}

export interface CreateDisruptionBody {
  readonly type: DisruptionType;
  readonly description: string;
  readonly sectionId: SectionId;
  readonly estimatedDuration: TimeInterval;
  readonly criticality: Criticality;
}

export interface UpdateDisruptionBody {
  readonly status?: IncidentStatus;
  readonly actualDuration?: TimeInterval;
  readonly resolvedNote?: string;
}

export interface ImpactAnalysisRequest {
  readonly disruptionId: DisruptionId;
  readonly planId: PlanId;
  readonly scenarioContext?: ScenarioContext;
}
