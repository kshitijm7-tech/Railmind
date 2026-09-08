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
  TrainService, 
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

export class MockNetworkService implements INetworkService {
  async getNetwork(): Promise<RailwayNetwork> {
    return Promise.resolve(DEMO_NETWORK);
  }
  async getStateMetadata(): Promise<RailwayStateMetadata> {
    return Promise.resolve(DEMO_STATE_METADATA);
  }
}

export class MockMaintenanceService implements IMaintenanceService {
  async getTasks(): Promise<MaintenanceTask[]> {
    return Promise.resolve(DEMO_MAINTENANCE_TASKS);
  }
  async getTaskById(id: string): Promise<MaintenanceTask | null> {
    const task = DEMO_MAINTENANCE_TASKS.find(t => t.task_id === id) || null;
    return Promise.resolve(task);
  }
}

export class MockTrainService implements ITrainService {
  async getTrains(): Promise<TrainService[]> {
    return Promise.resolve(DEMO_TRAINS);
  }
  async getTrainById(id: string): Promise<TrainService | null> {
    const train = DEMO_TRAINS.find(t => t.train_id === id) || null;
    return Promise.resolve(train);
  }
}

export class MockPlanningService implements IPlanningService {
  async getCandidateWindows(): Promise<CandidateBlockWindow[]> {
    return Promise.resolve(DEMO_CANDIDATE_WINDOWS);
  }
  async getPlans(): Promise<Plan[]> {
    return Promise.resolve(DEMO_PLANS);
  }
  async getPlanById(id: string): Promise<Plan | null> {
    const plan = DEMO_PLANS.find(p => p.plan_id === id) || null;
    return Promise.resolve(plan);
  }
  async generatePlan(strategy: string): Promise<Plan> {
    const basePlan = DEMO_PLANS[0];
    return Promise.resolve({
      ...basePlan,
      plan_id: `PLAN-GEN-${Date.now()}`,
      name: `Generated Plan (${strategy})`,
      created_at: new Date().toISOString() as any
    });
  }
}

export class MockSimulationService implements ISimulationService {
  async getScenarios(): Promise<Scenario[]> {
    return Promise.resolve(DEMO_SCENARIOS);
  }
  async runSimulation(scenarioId: string, planId: string): Promise<SimulationResult> {
    return Promise.resolve({
      simulation_id: `SIM-${Date.now()}`,
      scenario_id: scenarioId,
      plan_id: planId,
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
  async getActiveIncidents(): Promise<Incident[]> {
    return Promise.resolve(DEMO_INCIDENTS);
  }
  async getIncidentById(id: string): Promise<Incident | null> {
    const inc = DEMO_INCIDENTS.find(i => i.incident_id === id) || null;
    return Promise.resolve(inc);
  }
}

export class MockRecommendationService implements IRecommendationService {
  async getLatestRecommendation(): Promise<Recommendation | null> {
    return Promise.resolve(DEMO_RECOMMENDATION);
  }
  async getRecommendationById(id: string): Promise<Recommendation | null> {
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
}

export class MockAuditService implements IAuditService {
  async getAuditEvents(): Promise<AuditEvent[]> {
    return Promise.resolve(DEMO_AUDIT_EVENTS);
  }
}

export class MockSearchService implements ISearchService {
  async search(query: string): Promise<SearchResultItem[]> {
    if (!query || query.trim() === '') {
      return Promise.resolve([]);
    }
    const q = query.toLowerCase();
    const results: SearchResultItem[] = [];

    // Search Trains
    DEMO_TRAINS.forEach(t => {
      if (t.train_number.toLowerCase().includes(q) || t.name.toLowerCase().includes(q)) {
        results.push({
          id: t.train_id,
          title: `${t.train_number} - ${t.name}`,
          subtitle: `${t.train_type} · Priority ${t.priority}`,
          category: 'TRAIN',
          url: `/trains?id=${t.train_id}`,
          statusTone: t.current_status === 'ON_TIME' ? 'approved' : 'warning',
          badge: t.current_status
        });
      }
    });

    // Search Tasks
    DEMO_MAINTENANCE_TASKS.forEach(t => {
      if (t.task_id.toLowerCase().includes(q) || t.title.toLowerCase().includes(q) || t.department.toLowerCase().includes(q)) {
        results.push({
          id: t.task_id,
          title: `${t.task_id}: ${t.title}`,
          subtitle: `${t.department} · ${t.section_id} · Priority ${t.priority_score.toFixed(0)}`,
          category: 'MAINTENANCE_TASK',
          url: `/maintenance?id=${t.task_id}`,
          statusTone: t.criticality === 'CRITICAL' ? 'critical' : 'attention',
          badge: t.criticality
        });
      }
    });

    // Search Sections
    DEMO_NETWORK.sections.forEach(s => {
      if (s.section_id.toLowerCase().includes(q) || s.name.toLowerCase().includes(q)) {
        results.push({
          id: s.section_id,
          title: `${s.section_id}: ${s.name}`,
          subtitle: `${s.length_km}km · Max ${s.max_speed_kmph}km/h · ${s.department_owners.join(', ')}`,
          category: 'SECTION',
          url: `/operations?section=${s.section_id}`,
          statusTone: 'neutral',
          badge: s.criticality
        });
      }
    });

    // Search Incidents
    DEMO_INCIDENTS.forEach(inc => {
      if (inc.incident_id.toLowerCase().includes(q) || inc.title.toLowerCase().includes(q)) {
        results.push({
          id: inc.incident_id,
          title: `${inc.incident_id}: ${inc.title}`,
          subtitle: `Severity ${inc.severity} · ${inc.section_id}`,
          category: 'INCIDENT',
          url: `/disruptions?id=${inc.incident_id}`,
          statusTone: 'critical',
          badge: inc.status
        });
      }
    });

    return Promise.resolve(results);
  }
}
