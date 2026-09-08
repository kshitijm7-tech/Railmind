import { ISOTimestamp } from './ids';

export interface TimeInterval {
  readonly start: ISOTimestamp;
  readonly end: ISOTimestamp;
}

export interface DurationMinutes {
  readonly expected: number;
  readonly minimum: number;
  readonly maximum: number;
}

export interface PlanningHorizon {
  readonly start: ISOTimestamp;
  readonly end: ISOTimestamp;
  readonly horizonHours: number;
}

export interface ScheduledTiming {
  readonly scheduled: ISOTimestamp;
  readonly actual?: ISOTimestamp;
  readonly delayMinutes: number;
}
