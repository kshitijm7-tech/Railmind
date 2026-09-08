import { ISOTimestamp } from '../common/ids';
import { Provenance } from '../common/provenance';

export interface PredictionBase {
  readonly model_id: string;
  readonly model_version: string;
  readonly confidence: number;
  readonly generated_at: ISOTimestamp;
  readonly provenance: Provenance;
}

export interface PriorityPrediction extends PredictionBase {
  readonly task_id: string;
  readonly predicted_priority_score: number;
  readonly contributing_factors: Record<string, number>;
}

export interface DurationPrediction extends PredictionBase {
  readonly task_id: string;
  readonly predicted_duration_minutes: number;
  readonly p10_minutes: number;
  readonly p90_minutes: number;
}

export interface DelayPrediction extends PredictionBase {
  readonly train_id: string;
  readonly section_id: string;
  readonly predicted_delay_minutes: number;
}

export interface FailureRiskPrediction extends PredictionBase {
  readonly asset_id: string;
  readonly probability_of_failure: number;
  readonly time_horizon_hours: number;
}
