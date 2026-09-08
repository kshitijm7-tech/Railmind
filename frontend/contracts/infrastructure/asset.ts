import { AssetId, StationId, SectionId } from '../common/ids';
import { Criticality } from '../common/enums';
export type AssetCategory = 'TRACK' | 'SIGNAL' | 'OHE' | 'POINT' | 'BRIDGE' | 'LEVEL_CROSSING';

export interface RailwayAsset {
  readonly asset_id: AssetId;
  readonly category: AssetCategory;
  readonly name: string;
  readonly location_section?: SectionId;
  readonly location_station?: StationId;
  readonly criticality: Criticality;
  readonly is_operational: boolean;
}
