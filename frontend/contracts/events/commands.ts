import { ISOTimestamp } from '../common/ids';

export interface Command<T> {
  readonly command_id: string;
  readonly command_type: string;
  readonly requested_at: ISOTimestamp;
  readonly requested_by: string;
  readonly payload: T;
}
