import { ISOTimestamp } from '../../common/ids';
import { PaginationParams, SortParams } from '../common/envelope';

export interface AuditEventListQuery extends PaginationParams, SortParams {
  readonly entityId?: string;
  readonly entityType?: string;
  readonly eventType?: string;
  readonly actor?: string;
  readonly from?: ISOTimestamp;
  readonly to?: ISOTimestamp;
}
