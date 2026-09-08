import { TrainId, StationId, SectionId } from '../common/ids';
import { ScheduledTiming } from '../common/time';

export type TrainType = 'EXPRESS' | 'PASSENGER' | 'FREIGHT' | 'MAINTENANCE';

export interface SectionTiming {
  readonly section_id: SectionId;
  readonly entry_time: ScheduledTiming;
  readonly exit_time: ScheduledTiming;
}

export interface TrainService {
  readonly train_id: TrainId;
  readonly name: string;
  readonly train_number: string;
  readonly type: TrainType;
  readonly origin_station_id: StationId;
  readonly destination_station_id: StationId;
  readonly sections: SectionTiming[];
}

export interface Train {
  readonly service: TrainService;
  readonly max_speed_kmh: number;
  readonly length_m: number;
  readonly weight_t: number;
  readonly priority: number;
}
