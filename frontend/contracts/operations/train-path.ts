import { TrainId, SectionId } from '../common/ids';
import { TimeInterval } from '../common/time';

export interface PathConstraint {
  readonly type: string;
  readonly description: string;
}

export interface PathSegment {
  readonly section_id: SectionId;
  readonly interval: TimeInterval;
  readonly is_conflicted: boolean;
}

export interface TrainPath {
  readonly train_id: TrainId;
  readonly segments: PathSegment[];
  readonly constraints: PathConstraint[];
  readonly is_valid: boolean;
}
