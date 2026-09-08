import { SectionId, StationId } from '../common/ids';

export interface TrackSection {
  readonly section_id: SectionId;
  readonly name: string;
  readonly start_station_id: StationId;
  readonly end_station_id: StationId;
  readonly length_km: number;
  readonly max_speed_kmh: number;
  readonly is_electrified: boolean;
  readonly is_bidirectional: boolean;
  readonly track_count: number;
}
