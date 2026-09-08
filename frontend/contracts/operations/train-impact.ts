import { TrainId, BlockId } from '../common/ids';
import { RiskLevel } from '../common/enums';

export type ImpactType = 'DELAY' | 'CANCELLATION' | 'REROUTING' | 'HOLD' | 'PATH_CHANGE';

export interface TrainImpact {
  readonly train_id: TrainId;
  readonly block_id: BlockId;
  readonly impact_type: ImpactType;
  readonly delay_minutes: number;
  readonly is_rerouted: boolean;
  readonly is_cancelled: boolean;
  readonly reroute_description?: string;
  readonly severity: RiskLevel;
  readonly reason: string;
  readonly cascading_delay_minutes: number;
}
