import { SimulationRunId, ScenarioId, ISOTimestamp } from '../common/ids';
import { TimeInterval } from '../common/time';
import { SimulationResult } from './simulation-result';

export type SimulationStatus = 'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';

export interface SimulationRun {
  readonly run_id: SimulationRunId;
  readonly scenario_id: ScenarioId;
  readonly status: SimulationStatus;
  readonly requested_at: ISOTimestamp;
  readonly completed_at?: ISOTimestamp;
  readonly simulated_horizon: TimeInterval;
  readonly progress_percent: number;
  readonly error_message?: string;
  readonly result?: SimulationResult;
}
