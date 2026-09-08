import { TrainId, SectionId, BlockId, ISOTimestamp } from '../../common/ids';
import { PaginationParams, SortParams, DateRangeFilter, ScenarioContext } from '../common/envelope';
import { TrainType, TrainStatus } from '../../operations/train';
import { ImpactType } from '../../operations/train-impact';

export interface TrainListQuery extends PaginationParams, SortParams {
  readonly status?: TrainStatus;
  readonly trainType?: TrainType;
  readonly sectionId?: SectionId;
  readonly scenarioContext?: ScenarioContext;
}

export interface TrainPathListQuery extends PaginationParams {
  readonly trainId?: TrainId;
  readonly sectionId?: SectionId;
  readonly from?: ISOTimestamp;
  readonly to?: ISOTimestamp;
}

export interface OperationalWindowListQuery extends PaginationParams, DateRangeFilter {
  readonly sectionId?: SectionId;
  readonly minDurationMin?: number;
  readonly scenarioContext?: ScenarioContext;
}

export interface TrainImpactListQuery extends PaginationParams {
  readonly trainId?: TrainId;
  readonly blockId?: BlockId;
  readonly impactType?: ImpactType;
  readonly scenarioContext?: ScenarioContext;
}
