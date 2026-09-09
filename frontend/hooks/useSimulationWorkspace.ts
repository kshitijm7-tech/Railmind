import type { PlanId, ScenarioId } from '../contracts/common/ids';
import type { RunSimulationRequest } from '../contracts/api/simulation/requests';
import type { Plan, Scenario, SimulationResult } from '../domain';

/**
 * Build a governed run request. Simulations always execute inside an explicit
 * scenario boundary — never against silent LIVE state.
 */
export function buildRunRequest(planId: string, scenarioId: string): RunSimulationRequest {
  return {
    planId: planId as PlanId,
    scenarioId: scenarioId as ScenarioId,
    scenarioContext: { mode: 'SCENARIO', scenarioId: scenarioId as ScenarioId },
  };
}

export interface SimulationSummary {
  delayMinutes: number;
  affectedTrains: string[];
  affectedBlocks: string[];
  completionPct: number;
  overrunProbabilityPct: number;
  expectedMeanDelayMin: number;
  p90DelayMin: number;
  iterations: number;
  riskLevel: SimulationResult['risk_level'];
}

/** Pure projection of backend simulation output. No values are invented. */
export function summarizeSimulation(result: SimulationResult): SimulationSummary {
  return {
    delayMinutes: result.total_delay_minutes,
    affectedTrains: result.affected_train_ids,
    affectedBlocks: result.affected_block_ids,
    completionPct: Math.round(result.maintenance_completion_rate * 100),
    overrunProbabilityPct: Math.round(result.monte_carlo.p_any_violation * 100),
    expectedMeanDelayMin: result.monte_carlo.expected_mean_delay_min,
    p90DelayMin: result.monte_carlo.p90_delay_min,
    iterations: result.monte_carlo.iterations,
    riskLevel: result.risk_level,
  };
}

export interface SimulationDefaults {
  planId: string | null;
  scenarioId: string | null;
}

/** Default selections are first-available, never ranked or scored. */
export function selectDefaults(scenarios: Scenario[], plans: Plan[]): SimulationDefaults {
  return {
    planId: plans.length > 0 ? plans[0].plan_id : null,
    scenarioId: scenarios.length > 0 ? scenarios[0].scenario_id : null,
  };
}

/** A result is usable only when the service returns a non-null payload. */
export function hasUsableResult(result: SimulationResult | null): result is SimulationResult {
  return result !== null;
}
