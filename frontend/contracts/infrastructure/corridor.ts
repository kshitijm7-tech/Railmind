import { CorridorId, StationId, SectionId } from '../common/ids';
import { TrackSection } from './track-section';
import { RailwayAsset } from './asset';

export interface Station {
  readonly station_id: StationId;
  readonly name: string;
  readonly code: string;
  readonly latitude: number;
  readonly longitude: number;
  readonly platform_count: number;
}

export interface Corridor {
  readonly corridor_id: CorridorId;
  readonly name: string;
  readonly start_station_id: StationId;
  readonly end_station_id: StationId;
  readonly sections: SectionId[];
}

export interface RailwayNetwork {
  readonly stations: Station[];
  readonly sections: TrackSection[];
  readonly corridors: Corridor[];
  readonly assets: RailwayAsset[];
}
