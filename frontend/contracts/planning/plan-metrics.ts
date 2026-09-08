export interface ObjectiveTerm {
  readonly name: string;
  readonly value: number;
  readonly weight: number;
}

export interface PlanMetrics {
  readonly total_maintenance_time_minutes: number;
  readonly total_train_delay_minutes: number;
  readonly constraints_violated: number;
  readonly resource_utilization_percent: number;
  readonly objective_terms?: ObjectiveTerm[];
  readonly overall_score?: number;
}
