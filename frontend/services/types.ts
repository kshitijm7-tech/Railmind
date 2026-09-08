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
} from '../domain';

export interface INetworkService {
  getNetwork(): Promise<RailwayNetwork>;
  getStateMetadata(): Promise<RailwayStateMetadata>;
}

export interface IMaintenanceService {
  getTasks(): Promise<MaintenanceTask[]>;
  getTaskById(id: string): Promise<MaintenanceTask | null>;
}

export interface ITrainService {
  getTrains(): Promise<TrainService[]>;
  getTrainById(id: string): Promise<TrainService | null>;
}

export interface IPlanningService {
  getCandidateWindows(): Promise<CandidateBlockWindow[]>;
  getPlans(): Promise<Plan[]>;
  getPlanById(id: string): Promise<Plan | null>;
  generatePlan(strategy: string): Promise<Plan>;
}

export interface ISimulationService {
  getScenarios(): Promise<Scenario[]>;
  runSimulation(scenarioId: string, planId: string): Promise<SimulationResult>;
}

export interface IDisruptionService {
  getActiveIncidents(): Promise<Incident[]>;
  getIncidentById(id: string): Promise<Incident | null>;
}

export interface IRecommendationService {
  getLatestRecommendation(): Promise<Recommendation | null>;
  getRecommendationById(id: string): Promise<Recommendation | null>;
}

export interface IDecisionService {
  submitDecision(record: Omit<DecisionRecord, 'decision_id' | 'timestamp'>): Promise<DecisionRecord>;
  getDecisionHistory(): Promise<DecisionRecord[]>;
}

export interface IAuditService {
  getAuditEvents(): Promise<AuditEvent[]>;
}

export interface ISearchService {
  search(query: string): Promise<SearchResultItem[]>;
}
