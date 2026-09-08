import { Criticality, Department } from '../../contracts/common/enums';
import { ISOTimestamp } from '../../contracts/common/ids';
export type { Criticality, Department };

export interface Station {
  station_id: string;
  name: string;
  code: string;
  platforms: number;
  tracks: number;
  is_junction: boolean;
}

export interface Section {
  section_id: string;
  name: string;
  from_station_id: string;
  to_station_id: string;
  length_km: number;
  track_count: number;
  max_speed_kmph: number;
  department_owners: Department[];
  criticality: Criticality;
  status: 'OPERATIONAL' | 'RESTRICTED' | 'BLOCKED' | 'MAINTENANCE';
}

export interface RailwayAsset {
  asset_id: string;
  asset_type: 'TrackAsset' | 'SignalAsset' | 'OHEAsset' | 'Bridge' | 'ElectricalAsset';
  name: string;
  section_id: string;
  department: Department;
  health_score: number; // 0-100
  criticality: Criticality;
  last_inspected: ISOTimestamp;
  next_due: ISOTimestamp;
  status: 'HEALTHY' | 'DEGRADED' | 'DEFECTIVE' | 'CRITICAL';
}

export interface RailwayNetwork {
  zone: string;
  division: string;
  corridor: string;
  stations: Station[];
  sections: Section[];
  assets: RailwayAsset[];
}
