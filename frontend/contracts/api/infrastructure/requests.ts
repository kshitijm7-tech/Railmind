import { CorridorId, SectionId } from '../../common/ids';
import { Criticality, Department } from '../../common/enums';
import { PaginationParams, SortParams } from '../common/envelope';
import { AssetCategory, AssetOperationalStatus } from '../../infrastructure/asset';
import { SectionStatus } from '../../infrastructure/track-section';

export interface AssetListQuery extends PaginationParams, SortParams {
  readonly sectionId?: SectionId;
  readonly department?: Department;
  readonly criticality?: Criticality;
  readonly category?: AssetCategory;
  readonly status?: AssetOperationalStatus;
}

export interface TrackSectionListQuery extends PaginationParams, SortParams {
  readonly corridorId?: CorridorId;
  readonly status?: SectionStatus;
}

export interface CorridorListQuery extends PaginationParams {
  readonly zone?: string;
}
