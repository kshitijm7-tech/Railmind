export type TrainType = 'Passenger' | 'Goods' | 'Special';

export interface SectionTiming {
  section_id: string;
  scheduled_entry: string;
  scheduled_exit: string;
  actual_or_simulated_entry?: string;
  actual_or_simulated_exit?: string;
  delay_minutes: number;
}

export interface TrainService {
  train_id: string;
  train_number: string;
  name: string;
  train_type: TrainType;
  priority: number; // 1 (highest) to 5
  origin_station_id: string;
  destination_station_id: string;
  route_section_ids: string[];
  schedule: SectionTiming[];
  current_status: 'ON_TIME' | 'DELAYED' | 'HELD' | 'REROUTED' | 'CANCELLED';
  current_delay_min: number;
  cascading_delay_estimate_min: number;
}
