import { Department } from './network';

export interface CrewPool {
  pool_id: string;
  department: Department;
  shift_name: 'Morning' | 'Night';
  shift_window_start: string;
  shift_window_end: string;
  total_crew: number;
  available_crew: number;
  assigned_crew: number;
}

export interface HeavyMachinery {
  machine_id: string;
  name: string;
  machinery_type: 'TrackRelayTrain' | 'BallastTamper' | 'TowerWagon' | 'Crane';
  department: Department;
  current_location_station_id: string;
  status: 'AVAILABLE' | 'DEPLOYED' | 'MAINTENANCE';
}
