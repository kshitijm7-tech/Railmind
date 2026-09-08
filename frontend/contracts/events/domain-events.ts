import { EventId, ISOTimestamp } from '../common/ids';
import { Provenance } from '../common/provenance';

export interface EventEnvelope<T> {
  readonly event_id: EventId;
  readonly event_type: string;
  readonly timestamp: ISOTimestamp;
  readonly provenance: Provenance;
  readonly payload: T;
}

export interface BlockApprovedEvent {
  readonly block_id: string;
  readonly approved_by: string;
}

export interface DisruptionReportedEvent {
  readonly disruption_id: string;
  readonly section_id: string;
  readonly severity: string;
}
