import { DisruptionId, PlanId } from '../../common/ids';
import { ScenarioContext } from '../common/envelope';

export interface AnalyzeRecoveryRequest {
  readonly disruptionId: DisruptionId;
  readonly planId: PlanId;
  readonly scenarioContext: ScenarioContext; // required — recovery always scoped
}

export interface RecoveryCandidatesRequest {
  readonly disruptionId: DisruptionId;
  readonly planId: PlanId;
  readonly maxCandidates?: number; // default: 3
  readonly scenarioContext: ScenarioContext;
}

export interface RecoveryReplanRequest {
  readonly disruptionId: DisruptionId;
  readonly planId: PlanId;
  readonly selectedCandidateId: string;
  readonly scenarioContext: ScenarioContext;
  readonly idempotencyKey?: string;
}
