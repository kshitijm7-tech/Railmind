import { WindowId, SectionId } from '../common/ids';
import { TimeInterval } from '../common/time';

export type WindowAvailability = 'AVAILABLE' | 'OCCUPIED' | 'MAINTENANCE' | 'CLOSED';

export interface OperationalWindow {
  readonly window_id: WindowId;
  readonly section_id: SectionId;
  readonly interval: TimeInterval;
  readonly availability: WindowAvailability;
  readonly max_trains: number;
  readonly currently_assigned_trains: number;
}
