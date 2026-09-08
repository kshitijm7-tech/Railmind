export type ScenarioType = 
  | 'DURATION_OVERRUN' 
  | 'BLOCK_CANCELLATION' 
  | 'PRIORITY_TRAIN' 
  | 'INFRASTRUCTURE_LOSS' 
  | 'RESOURCE_LOSS' 
  | 'WINDOW_CHANGE' 
  | 'TRAIN_DELAY';

export interface Scenario {
  scenario_id: string;
  name: string;
  scenario_type: ScenarioType;
  base_state_version: string;
  description: string;
  parameters: Record<string, any>;
  created_at: string;
}

export interface MonteCarloSummary {
  iterations: number;
  p_any_violation: number;
  p_overrun_by_block: Record<string, number>;
  expected_mean_delay_min: number;
  p90_delay_min: number;
}

export interface SimulationResult {
  simulation_id: string;
  scenario_id: string;
  plan_id: string;
  total_delay_minutes: number;
  affected_train_ids: string[];
  affected_block_ids: string[];
  maintenance_completion_rate: number;
  monte_carlo: MonteCarloSummary;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
}
