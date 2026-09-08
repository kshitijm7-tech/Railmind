import { PlanId, ScenarioId } from '../../common/ids';
import { ScenarioContext } from '../common/envelope';

export interface RunSimulationRequest {
  readonly planId: PlanId;
  readonly scenarioId: ScenarioId;
  readonly scenarioContext: ScenarioContext; // required — must carry scenario boundary
  readonly assumptions?: Record<string, unknown>;
  readonly idempotencyKey?: string;
}

export interface SimulationListQuery {
  readonly planId?: PlanId;
  readonly scenarioId?: ScenarioId;
  readonly page?: number;
  readonly pageSize?: number;
}
