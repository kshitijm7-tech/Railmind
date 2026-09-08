export interface SimulationMetric {
  readonly name: string;
  readonly value: number;
  readonly unit: string;
}

export interface MonteCarloSummary {
  readonly p50: number;
  readonly p90: number;
  readonly p99: number;
  readonly samples: number;
}

export interface SimulationResult {
  readonly is_feasible: boolean;
  readonly total_delay_minutes: number;
  readonly total_delay_p90_minutes?: number;
  readonly cancelled_trains: number;
  readonly delayed_trains: number;
  readonly bottleneck_sections: string[];
  readonly constraint_violations: string[];
  readonly metrics: SimulationMetric[];
  readonly delay_distribution?: MonteCarloSummary;
}
