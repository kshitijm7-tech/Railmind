import { 
  INetworkService, 
  IMaintenanceService, 
  ITrainService, 
  IPlanningService, 
  ISimulationService, 
  IDisruptionService, 
  IRecommendationService, 
  IDecisionService, 
  IAuditService, 
  ISearchService 
} from '../types';

import {
  DEMO_NETWORK,
  DEMO_STATE_METADATA,
  DEMO_MAINTENANCE_TASKS,
  DEMO_TRAINS,
  DEMO_CANDIDATE_WINDOWS,
  DEMO_PLANS,
  DEMO_RECOMMENDATION,
  DEMO_INCIDENTS,
  DEMO_SCENARIOS,
  DEMO_AUDIT_EVENTS
} from '../../fixtures/demoCorridor';

import { 
  RailwayNetwork, 
  RailwayStateMetadata, 
  MaintenanceTask, 
  TrainService as TrainServiceDomain, 
  CandidateBlockWindow, 
  Plan, 
  Recommendation, 
  Incident, 
  Scenario, 
  SimulationResult, 
  DecisionRecord, 
  AuditEvent,
  SearchResultItem
} from '../../domain';

import { TaskId, TrainId, PlanId, DisruptionId, DecisionId, RecommendationId, makeTimestamp } from '../../contracts/common/ids';
import { MaintenanceTaskListQuery, CreateMaintenanceTaskBody, DefectListQuery } from '../../contracts/api/maintenance';
import { TrainListQuery } from '../../contracts/api/operations';
import { PlanListQuery, GeneratePlanRequest, BlockListQuery, ComparePlansRequest } from '../../contracts/api/planning';
import { RunSimulationRequest } from '../../contracts/api/simulation';
import { DisruptionListQuery, CreateDisruptionBody } from '../../contracts/api/disruption';
import { ApproveDecisionBody, RejectDecisionBody, DeferDecisionBody } from '../../contracts/api/decision';
import { AuditEventListQuery } from '../../contracts/api/audit';
import { AsyncJob } from '../../contracts/api/common/job';

export class MockNetworkService implements INetworkService {
  async getNetwork(): Promise<RailwayNetwork> {
    return Promise.resolve(DEMO_NETWORK);
  }
  async getStateMetadata(): Promise<RailwayStateMetadata> {
    return Promise.resolve(DEMO_STATE_METADATA);
  }
}

export class MockMaintenanceService implements IMaintenanceService {
  async getTasks(query?: MaintenanceTaskListQuery): Promise<MaintenanceTask[]> {
    return Promise.resolve(DEMO_MAINTENANCE_TASKS);
  }
  async getTaskById(id: TaskId): Promise<MaintenanceTask | null> {
    const task = DEMO_MAINTENANCE_TASKS.find(t => t.task_id === id) || null;
    return Promise.resolve(task);
  }
  async createTask(body: CreateMaintenanceTaskBody): Promise<MaintenanceTask> {
    return Promise.resolve({
      ...DEMO_MAINTENANCE_TASKS[0],
      task_id: `TASK-MOCK-${Date.now()}` as any,
      title: body.description,
      department: body.department,
      criticality: body.criticality,
    });
  }
  async getDefects(query?: DefectListQuery): Promise<Incident[]> {
    return Promise.resolve([]);
  }
}

export class MockTrainService implements ITrainService {
  async getTrains(query?: TrainListQuery): Promise<TrainServiceDomain[]> {
    return Promise.resolve(DEMO_TRAINS);
  }
  async getTrainById(id: TrainId): Promise<TrainServiceDomain | null> {
    const train = DEMO_TRAINS.find(t => t.train_id === id) || null;
    return Promise.resolve(train);
  }
}

export class MockPlanningService implements IPlanningService {
  async getCandidateWindows(query?: BlockListQuery): Promise<CandidateBlockWindow[]> {
    return Promise.resolve(DEMO_CANDIDATE_WINDOWS);
  }
  async getPlans(query?: PlanListQuery): Promise<Plan[]> {
    return Promise.resolve(DEMO_PLANS);
  }
  async getPlanById(id: PlanId): Promise<Plan | null> {
    const plan = DEMO_PLANS.find(p => p.plan_id === id) || null;
    return Promise.resolve(plan);
  }
  async generatePlan(request: GeneratePlanRequest): Promise<AsyncJob> {
    return Promise.resolve({
      jobId: `JOB-PLAN-${Date.now()}`,
      status: 'COMPLETED',
      requestedAt: makeTimestamp(new Date().toISOString()),
      completedAt: makeTimestamp(new Date().toISOString()),
      progressPercent: 100,
      resultEndpoint: '/api/v1/plans/PLAN-GEN-MOCK'
    });
  }
  async comparePlans(request: ComparePlansRequest): Promise<Plan[]> {
    return Promise.resolve(DEMO_PLANS.slice(0, 2));
  }
}

export class MockSimulationService implements ISimulationService {
  async getScenarios(): Promise<Scenario[]> {
    return Promise.resolve(DEMO_SCENARIOS);
  }
  async runSimulation(request: RunSimulationRequest): Promise<AsyncJob> {
    return Promise.resolve({
      jobId: `JOB-SIM-${Date.now()}`,
      status: 'COMPLETED',
      requestedAt: makeTimestamp(new Date().toISOString()),
      completedAt: makeTimestamp(new Date().toISOString()),
      progressPercent: 100,
      resultEndpoint: `/api/v1/simulations/SIM-MOCK/result`
    });
  }
  async getSimulationResult(simulationId: string): Promise<SimulationResult | null> {
    return Promise.resolve({
      simulation_id: simulationId,
      scenario_id: 'SCENARIO-1',
      plan_id: 'PLAN-1',
      total_delay_minutes: 48,
      affected_train_ids: ['TRN-12001', 'TRN-12952'],
      affected_block_ids: ['BLK-04-01'],
      maintenance_completion_rate: 0.75,
      monte_carlo: {
        iterations: 200,
        p_any_violation: 0.38,
        p_overrun_by_block: { 'BLK-04-01': 0.38 },
        expected_mean_delay_min: 44.5,
        p90_delay_min: 62.0
      },
      risk_level: 'HIGH'
    });
  }
}

export class MockDisruptionService implements IDisruptionService {
  async getActiveIncidents(query?: DisruptionListQuery): Promise<Incident[]> {
    return Promise.resolve(DEMO_INCIDENTS);
  }
  async getIncidentById(id: DisruptionId): Promise<Incident | null> {
    const inc = DEMO_INCIDENTS.find(i => i.incident_id === id) || null;
    return Promise.resolve(inc);
  }
  async createDisruption(body: CreateDisruptionBody): Promise<Incident> {
    return Promise.resolve({
      ...DEMO_INCIDENTS[0],
      incident_id: `INC-MOCK-${Date.now()}`,
      title: body.description,
      status: 'Detected'
    });
  }
}

export class MockRecommendationService implements IRecommendationService {
  async getLatestRecommendation(): Promise<Recommendation | null> {
    return Promise.resolve(DEMO_RECOMMENDATION);
  }
  async getRecommendationById(id: RecommendationId): Promise<Recommendation | null> {
    if (id === DEMO_RECOMMENDATION.recommendation_id) {
      return Promise.resolve(DEMO_RECOMMENDATION);
    }
    return Promise.resolve(null);
  }
}

const mockDecisionsStore: DecisionRecord[] = [];

export class MockDecisionService implements IDecisionService {
  async submitDecision(record: Omit<DecisionRecord, 'decision_id' | 'timestamp'>): Promise<DecisionRecord> {
    const fullRecord: DecisionRecord = {
      ...record,
      decision_id: `DEC-${Date.now()}`,
      timestamp: new Date().toISOString() as any
    };
    mockDecisionsStore.push(fullRecord);
    return Promise.resolve(fullRecord);
  }
  async getDecisionHistory(): Promise<DecisionRecord[]> {
    return Promise.resolve(mockDecisionsStore);
  }
  async approveDecision(id: DecisionId, body: ApproveDecisionBody): Promise<DecisionRecord> {
    return this.submitDecision({ recommendation_id: 'rec1', plan_id: 'PLAN-1', state_version: 'v1', action: 'APPROVE', authorized_by: body.approver, user_role: 'Operations Controller', notes: body.justification });
  }
  async rejectDecision(id: DecisionId, body: RejectDecisionBody): Promise<DecisionRecord> {
    return this.submitDecision({ recommendation_id: 'rec1', plan_id: 'PLAN-1', state_version: 'v1', action: 'REJECT', authorized_by: body.approver, user_role: 'Operations Controller', notes: body.reason });
  }
  async deferDecision(id: DecisionId, body: DeferDecisionBody): Promise<DecisionRecord> {
    return this.submitDecision({ recommendation_id: 'rec1', plan_id: 'PLAN-1', state_version: 'v1', action: 'MODIFY', authorized_by: body.approver, user_role: 'Operations Controller', notes: body.reason });
  }
}

export class MockAuditService implements IAuditService {
  async getAuditEvents(query?: AuditEventListQuery): Promise<AuditEvent[]> {
    return Promise.resolve(DEMO_AUDIT_EVENTS);
  }
}

export class MockSearchService implements ISearchService {
  async search(query: string): Promise<SearchResultItem[]> {
    if (!query || query.trim() === '') return Promise.resolve([]);
    const q = query.toLowerCase();
    const results: SearchResultItem[] = [];
    DEMO_TRAINS.forEach(t => {
      if (t.train_number.toLowerCase().includes(q) || t.name.toLowerCase().includes(q)) {
        results.push({ id: t.train_id, title: `${t.train_number} - ${t.name}`, subtitle: `${t.train_type}`, category: 'TRAIN', url: `/trains?id=${t.train_id}`, statusTone: 'neutral', badge: t.current_status });
      }
    });
    return Promise.resolve(results);
  }
}
