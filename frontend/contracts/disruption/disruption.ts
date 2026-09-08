import { DisruptionId, SectionId, ISOTimestamp } from '../common/ids';
import { Criticality } from '../common/enums';
import { TimeInterval } from '../common/time';

export type DisruptionType = 'ASSET_FAILURE' | 'WEATHER' | 'CREW_SHORTAGE' | 'POWER_OUTAGE' | 'ACCIDENT' | 'OTHER';
export type IncidentStatus = 'REPORTED' | 'VERIFIED' | 'UNDER_REPAIR' | 'RESOLVED' | 'CLOSED';

export interface Disruption {
  readonly disruption_id: DisruptionId;
  readonly type: DisruptionType;
  readonly description: string;
  readonly section_id: SectionId;
  readonly estimated_duration: TimeInterval;
  readonly actual_duration?: TimeInterval;
  readonly status: IncidentStatus;
  readonly criticality: Criticality;
  readonly reported_at: ISOTimestamp;
  readonly resolved_at?: ISOTimestamp;
}
