/**
 * F01 — Mock/real service switching.
 *
 *                 Service Interface
 *                       |
 *             +---------+---------+
 *             v                   v
 *        Real API             Mock API
 *             |                   |
 *             +---------+---------+
 *                       v
 *                       UI
 *
 * The UI never branches on the data source. Mode is resolved once from
 * NEXT_PUBLIC_API_MODE (auto | real | mock):
 * - mock: always mock (offline/demo).
 * - real: always real (errors propagate, never silently mocked).
 * - auto: try real; fall back to mock only when the backend is unreachable
 *   (NETWORK/TIMEOUT/SERVER) or the capability has no backend endpoint
 *   (NOT_IMPLEMENTED). Validation/malformed responses never fall back —
 *   they surface so contract mismatches stay visible.
 */

import { getApiModeSetting, type ApiModeSetting } from './client/config';
import { RailmindApiError } from './client/errors';
import {
  MockAuditService,
  MockDecisionService,
  MockDisruptionService,
  MockMaintenanceService,
  MockNetworkService,
  MockPlanningService,
  MockRecommendationService,
  MockSearchService,
  MockSimulationService,
  MockTrainService,
} from '../mock/mockServices';
import type {
  IAuditService,
  IDecisionService,
  IDisruptionService,
  IMaintenanceService,
  INetworkService,
  IPlanningService,
  IRecommendationService,
  ISearchService,
  ISimulationService,
  ITrainService,
} from '../types';
import type { ServiceContainer } from '../types';
import { ApiDecisionService } from './decisionApiService';
import { ApiInfrastructureService } from './infrastructureApiService';
import { ApiMaintenanceService } from './maintenanceApiService';
import { ApiTrainService } from './operationsApiService';
import { ApiPlanningService } from './planningApiService';

export type ServiceMode = 'real' | 'mock';

const FALLBACK_KINDS = new Set(['NETWORK', 'TIMEOUT', 'SERVER', 'NOT_IMPLEMENTED']);

function shouldFallback(setting: ApiModeSetting, error: unknown): boolean {
  if (setting !== 'auto') return false;
  return error instanceof RailmindApiError && FALLBACK_KINDS.has(error.kind);
}

function withFallback<TArgs extends unknown[], TResult>(
  setting: ApiModeSetting,
  real: (...args: TArgs) => Promise<TResult>,
  mock: (...args: TArgs) => Promise<TResult>,
): (...args: TArgs) => Promise<TResult> {
  return async (...args: TArgs): Promise<TResult> => {
    if (setting === 'mock') return mock(...args);
    if (setting === 'real') return real(...args);
    try {
      return await real(...args);
    } catch (error: unknown) {
      if (shouldFallback(setting, error)) return mock(...args);
      throw error;
    }
  };
}

const mocks = {
  network: new MockNetworkService(),
  maintenance: new MockMaintenanceService(),
  trains: new MockTrainService(),
  planning: new MockPlanningService(),
  simulation: new MockSimulationService(),
  disruption: new MockDisruptionService(),
  recommendations: new MockRecommendationService(),
  decisions: new MockDecisionService(),
  audit: new MockAuditService(),
  search: new MockSearchService(),
};

const realNetwork = new ApiInfrastructureService();
const realMaintenance = new ApiMaintenanceService();
const realTrains = new ApiTrainService();
const realPlanning = new ApiPlanningService();
const realDecisions = new ApiDecisionService();

/**
 * No backend endpoints exist yet for simulation, disruption/recovery,
 * recommendations, audit, search, or state metadata (documented gaps), so
 * these are always mock-backed in F01. They stay behind the same interfaces
 * so F02+ can swap in real implementations without touching the UI.
 */
export function createServices(setting: ApiModeSetting = getApiModeSetting()): ServiceContainer {
  const network: INetworkService = {
    getNetwork: withFallback(setting, () => realNetwork.getNetwork(), () => mocks.network.getNetwork()),
    getStateMetadata: (...args) => mocks.network.getStateMetadata(...args),
  };
  const maintenance: IMaintenanceService = {
    getTasks: withFallback(setting, (q) => realMaintenance.getTasks(q), (q) => mocks.maintenance.getTasks(q)),
    getTaskById: withFallback(setting, (id) => realMaintenance.getTaskById(id), (id) => mocks.maintenance.getTaskById(id)),
    createTask: withFallback(setting, (b) => realMaintenance.createTask(b), (b) => mocks.maintenance.createTask(b)),
    getDefects: withFallback(setting, (q) => realMaintenance.getDefects(q), (q) => mocks.maintenance.getDefects(q)),
  };
  const trains: ITrainService = {
    getTrains: withFallback(setting, (q) => realTrains.getTrains(q), (q) => mocks.trains.getTrains(q)),
    getTrainById: withFallback(setting, (id) => realTrains.getTrainById(id), (id) => mocks.trains.getTrainById(id)),
  };
  const planning: IPlanningService = {
    getCandidateWindows: withFallback(
      setting,
      (q) => realPlanning.getCandidateWindows(q),
      (q) => mocks.planning.getCandidateWindows(q),
    ),
    getPlans: withFallback(setting, (q) => realPlanning.getPlans(q), (q) => mocks.planning.getPlans(q)),
    getPlanById: withFallback(setting, (id) => realPlanning.getPlanById(id), (id) => mocks.planning.getPlanById(id)),
    generatePlan: withFallback(setting, (r) => realPlanning.generatePlan(r), (r) => mocks.planning.generatePlan(r)),
    comparePlans: withFallback(setting, (r) => realPlanning.comparePlans(r), (r) => mocks.planning.comparePlans(r)),
  };
  const decisions: IDecisionService = {
    getDecisionHistory: withFallback(
      setting,
      () => realDecisions.getDecisionHistory(),
      () => mocks.decisions.getDecisionHistory(),
    ),
    approveDecision: withFallback(
      setting,
      (id, b) => realDecisions.approveDecision(id, b),
      (id, b) => mocks.decisions.approveDecision(id, b),
    ),
    rejectDecision: withFallback(
      setting,
      (id, b) => realDecisions.rejectDecision(id, b),
      (id, b) => mocks.decisions.rejectDecision(id, b),
    ),
    deferDecision: withFallback(
      setting,
      (id, b) => realDecisions.deferDecision(id, b),
      (id, b) => mocks.decisions.deferDecision(id, b),
    ),
    submitDecision: withFallback(
      setting,
      (r) => realDecisions.submitDecision(r),
      (r) => mocks.decisions.submitDecision(r),
    ),
  };

  const simulation: ISimulationService = mocks.simulation;
  const disruption: IDisruptionService = mocks.disruption;
  const recommendations: IRecommendationService = mocks.recommendations;
  const audit: IAuditService = mocks.audit;
  const search: ISearchService = mocks.search;

  return { network, maintenance, trains, planning, simulation, disruption, recommendations, decisions, audit, search };
}

export function getConfiguredApiMode(): ApiModeSetting {
  return getApiModeSetting();
}
