import { BlockId, SectionId, TaskId } from '../common/ids';
import { TimeInterval } from '../common/time';

export type BlockStatus = 'DRAFT' | 'REQUESTED' | 'APPROVED' | 'ACTIVE' | 'COMPLETED' | 'CANCELLED';

export interface CandidateBlockWindow {
  readonly interval: TimeInterval;
  readonly suitability_score: number;
  readonly conflicts: string[];
}

export interface Block {
  readonly block_id: BlockId;
  readonly section_id: SectionId;
  readonly interval: TimeInterval;
  readonly status: BlockStatus;
  readonly tasks: TaskId[];
  readonly required_power_off: boolean;
  readonly is_integrated: boolean;
}
