import { ScenarioId, PlanId, DisruptionId } from '../common/ids';

export type ScenarioType = 'BASELINE' | 'DISRUPTION' | 'MAINTENANCE_SHIFT' | 'RESOURCE_SHORTAGE';

export interface SimulationScenario {
  readonly scenario_id: ScenarioId;
  readonly base_plan_id: PlanId;
  readonly name: string;
  readonly type: ScenarioType;
  readonly disruptions: DisruptionId[];
  readonly description: string;
  readonly is_what_if: boolean;
}
