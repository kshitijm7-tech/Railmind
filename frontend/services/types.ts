import {
  MaintenanceTask,
  TrainService as TrainServiceDomain,
  Plan,
  Recommendation,
  Incident,
  Scenario,
  SimulationResult,
  DecisionRecord,
  AuditEvent,
  SearchResultItem,
  RailwayNetwork,
  RailwayStateMetadata,
  CandidateBlockWindow,
} from '../domain';
import { TaskId, TrainId, PlanId, DisruptionId, DecisionId, RecommendationId } from '../contracts/common/ids';
import { MaintenanceTaskListQuery, CreateMaintenanceTaskBody, DefectListQuery } from '../contracts/api/maintenance';
import { TrainListQuery } from '../contracts/api/operations';
import { PlanListQuery, GeneratePlanRequest, BlockListQuery, ComparePlansRequest } from '../contracts/api/planning';
import { RunSimulationRequest } from '../contracts/api/simulation';
import { DisruptionListQuery, CreateDisruptionBody } from '../contracts/api/disruption';
import { ApproveDecisionBody, RejectDecisionBody, DeferDecisionBody } from '../contracts/api/decision';
import { AuditEventListQuery } from '../contracts/api/audit';
import { AsyncJob } from '../contracts/api/common/job';

// INetworkService — unchanged, no pagination needed
export interface INetworkService {
  getNetwork(): Promise<RailwayNetwork>;
  getStateMetadata(): Promise<RailwayStateMetadata>;
}

// IMaintenanceService — upgraded to typed queries
export interface IMaintenanceService {
  getTasks(query?: MaintenanceTaskListQuery): Promise<MaintenanceTask[]>;
  getTaskById(id: TaskId): Promise<MaintenanceTask | null>;
  createTask(body: CreateMaintenanceTaskBody): Promise<MaintenanceTask>;
  getDefects(query?: DefectListQuery): Promise<Incident[]>; // using Incident as Defect proxy until backend
}

// ITrainService
export interface ITrainService {
  getTrains(query?: TrainListQuery): Promise<TrainServiceDomain[]>;
  getTrainById(id: TrainId): Promise<TrainServiceDomain | null>;
}

// IPlanningService — upgraded; generatePlan now returns AsyncJob
export interface IPlanningService {
  getCandidateWindows(query?: BlockListQuery): Promise<CandidateBlockWindow[]>;
  getPlans(query?: PlanListQuery): Promise<Plan[]>;
  getPlanById(id: PlanId): Promise<Plan | null>;
  generatePlan(request: GeneratePlanRequest): Promise<AsyncJob>;
  comparePlans(request: ComparePlansRequest): Promise<Plan[]>;
}

// ISimulationService — upgraded; runSimulation returns AsyncJob
export interface ISimulationService {
  getScenarios(): Promise<Scenario[]>;
  runSimulation(request: RunSimulationRequest): Promise<AsyncJob>;
  getSimulationResult(simulationId: string): Promise<SimulationResult | null>;
}

// IDisruptionService
export interface IDisruptionService {
  getActiveIncidents(query?: DisruptionListQuery): Promise<Incident[]>;
  getIncidentById(id: DisruptionId): Promise<Incident | null>;
  createDisruption(body: CreateDisruptionBody): Promise<Incident>;
}

// IRecommendationService
export interface IRecommendationService {
  getLatestRecommendation(): Promise<Recommendation | null>;
  getRecommendationById(id: RecommendationId): Promise<Recommendation | null>;
}

// IDecisionService — upgraded to typed action bodies
export interface IDecisionService {
  getDecisionHistory(): Promise<DecisionRecord[]>;
  approveDecision(id: DecisionId, body: ApproveDecisionBody): Promise<DecisionRecord>;
  rejectDecision(id: DecisionId, body: RejectDecisionBody): Promise<DecisionRecord>;
  deferDecision(id: DecisionId, body: DeferDecisionBody): Promise<DecisionRecord>;
  // backward compat shim for existing pages
  submitDecision(record: Omit<DecisionRecord, 'decision_id' | 'timestamp'>): Promise<DecisionRecord>;
}

// IAuditService
export interface IAuditService {
  getAuditEvents(query?: AuditEventListQuery): Promise<AuditEvent[]>;
}

// ISearchService — unchanged
export interface ISearchService {
  search(query: string): Promise<SearchResultItem[]>;
}
