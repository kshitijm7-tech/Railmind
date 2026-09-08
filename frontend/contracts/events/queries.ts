import { ISOTimestamp } from '../common/ids';

export interface Query<T> {
  readonly query_id: string;
  readonly query_type: string;
  readonly requested_at: ISOTimestamp;
  readonly params: T;
}
