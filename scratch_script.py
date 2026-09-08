import os

base = r"d:\Projects\Railmind\frontend\contracts"

files = {
    "common/ids.ts": """// Branded ID types — prevent accidental ID cross-assignment
export type ISOTimestamp = string & { readonly _brand: 'ISOTimestamp' };
export type TrainId = string & { readonly _brand: 'TrainId' };
export type AssetId = string & { readonly _brand: 'AssetId' };
export type SectionId = string & { readonly _brand: 'SectionId' };
export type BlockId = string & { readonly _brand: 'BlockId' };
export type TaskId = string & { readonly _brand: 'TaskId' };
export type PlanId = string & { readonly _brand: 'PlanId' };
export type ScenarioId = string & { readonly _brand: 'ScenarioId' };
export type DisruptionId = string & { readonly _brand: 'DisruptionId' };
export type DecisionId = string & { readonly _brand: 'DecisionId' };
export type RecommendationId = string & { readonly _brand: 'RecommendationId' };
export type EventId = string & { readonly _brand: 'EventId' };
export type CorridorId = string & { readonly _brand: 'CorridorId' };
export type StationId = string & { readonly _brand: 'StationId' };
export type DefectId = string & { readonly _brand: 'DefectId' };
export type WindowId = string & { readonly _brand: 'WindowId' };
export type RecoveryPlanId = string & { readonly _brand: 'RecoveryPlanId' };
export type SimulationRunId = string & { readonly _brand: 'SimulationRunId' };

// Factory functions (cast-safe)
export const makeTrainId = (s: string): TrainId => s as TrainId;
export const makeAssetId = (s: string): AssetId => s as AssetId;
export const makeSectionId = (s: string): SectionId => s as SectionId;
export const makeBlockId = (s: string): BlockId => s as BlockId;
export const makeTaskId = (s: string): TaskId => s as TaskId;
export const makePlanId = (s: string): PlanId => s as PlanId;
export const makeScenarioId = (s: string): ScenarioId => s as ScenarioId;
export const makeDisruptionId = (s: string): DisruptionId => s as DisruptionId;
export const makeDecisionId = (s: string): DecisionId => s as DecisionId;
export const makeRecommendationId = (s: string): RecommendationId => s as RecommendationId;
export const makeEventId = (s: string): EventId => s as EventId;
export const makeCorridorId = (s: string): CorridorId => s as CorridorId;
export const makeStationId = (s: string): StationId => s as StationId;
export const makeDefectId = (s: string): DefectId => s as DefectId;
export const makeWindowId = (s: string): WindowId => s as WindowId;
export const makeRecoveryPlanId = (s: string): RecoveryPlanId => s as RecoveryPlanId;
export const makeSimulationRunId = (s: string): SimulationRunId => s as SimulationRunId;
export const makeTimestamp = (s: string): ISOTimestamp => s as ISOTimestamp;
""",
    "common/time.ts": """import { ISOTimestamp } from './ids';

export interface TimeInterval {
  readonly start: ISOTimestamp;
  readonly end: ISOTimestamp;
}

export interface DurationMinutes {
  readonly expected: number;
  readonly minimum: number;
  readonly maximum: number;
}

export interface PlanningHorizon {
  readonly start: ISOTimestamp;
  readonly end: ISOTimestamp;
  readonly horizonHours: number;
}

export interface ScheduledTiming {
  readonly scheduled: ISOTimestamp;
  readonly actual?: ISOTimestamp;
  readonly delayMinutes: number;
}
""",
    "common/enums.ts": """export type Criticality = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type Department = 'Engineering' | 'S&T' | 'TRD' | 'OHE';
export type StateMode = 'LIVE' | 'SCENARIO';
export type StateType = 'PLAN' | 'ACTUAL' | 'PREDICTION' | 'SCENARIO';
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type UserRole = 'Operations Controller' | 'Planning Officer' | 'Senior Divisional Engineer';
""",
    "common/provenance.ts": """import { ISOTimestamp } from './ids';

export type DataSource = 'BDMS' | 'TMS' | 'SMMS' | 'TDMS' | 'COA' | 'USER' | 'AI' | 'SIMULATION' | 'SYNTHETIC' | 'IMPORT' | 'SYSTEM';
export type DataState = 'REAL' | 'MOCKED' | 'SIMULATED' | 'STUBBED' | 'PLANNED';

export interface Provenance {
  readonly source: DataSource;
  readonly state: DataState;
  readonly recordedAt: ISOTimestamp;
  readonly version?: string;
  readonly actor?: string;
}
""",
    "common/errors.ts": """import { ISOTimestamp } from './ids';

export type ErrorCategory = 'VALIDATION' | 'DOMAIN' | 'SYSTEM' | 'INTEGRATION' | 'AUTHORIZATION';
export type ErrorSeverity = 'INFO' | 'WARNING' | 'ERROR' | 'FATAL';

export interface DomainError {
  readonly code: string;
  readonly message: string;
  readonly category: ErrorCategory;
  readonly severity: ErrorSeverity;
  readonly field?: string;
  readonly details?: Record<string, unknown>;
  readonly correlationId?: string;
  readonly timestamp: ISOTimestamp;
}

// Stable machine-readable error codes
export const ERROR_CODES = {
  INVALID_TIME_INTERVAL: 'RAILMIND_001',
  INVALID_DURATION: 'RAILMIND_002',
  MISSING_REQUIRED_ID: 'RAILMIND_003',
  INVALID_LIFECYCLE_STATE: 'RAILMIND_004',
  INVALID_ENUM_VALUE: 'RAILMIND_005',
  CONFLICTING_BLOCK: 'RAILMIND_010',
  CONSTRAINT_VIOLATED: 'RAILMIND_011',
  PLAN_INVALIDATED: 'RAILMIND_020',
} as const;

export type ErrorCode = typeof ERROR_CODES[keyof typeof ERROR_CODES];
""",
    "common/index.ts": """export * from './ids';
export * from './time';
export * from './enums';
export * from './provenance';
export * from './errors';
""",
    "infrastructure/asset.ts": """import { AssetId, StationId, SectionId } from '../common/ids';
import { Criticality } from '../common/enums';
export type AssetCategory = 'TRACK' | 'SIGNAL' | 'OHE' | 'POINT' | 'BRIDGE' | 'LEVEL_CROSSING';

export interface RailwayAsset {
  readonly asset_id: AssetId;
  readonly category: AssetCategory;
  readonly name: string;
  readonly location_section?: SectionId;
  readonly location_station?: StationId;
  readonly criticality: Criticality;
  readonly is_operational: boolean;
}
""",
    "infrastructure/track-section.ts": """import { SectionId, StationId } from '../common/ids';

export interface TrackSection {
  readonly section_id: SectionId;
  readonly name: string;
  readonly start_station_id: StationId;
  readonly end_station_id: StationId;
  readonly length_km: number;
  readonly max_speed_kmh: number;
  readonly is_electrified: boolean;
  readonly is_bidirectional: boolean;
  readonly track_count: number;
}
""",
    "infrastructure/corridor.ts": """import { CorridorId, StationId, SectionId } from '../common/ids';
import { TrackSection } from './track-section';
import { RailwayAsset } from './asset';

export interface Station {
  readonly station_id: StationId;
  readonly name: string;
  readonly code: string;
  readonly latitude: number;
  readonly longitude: number;
  readonly platform_count: number;
}

export interface Corridor {
  readonly corridor_id: CorridorId;
  readonly name: string;
  readonly start_station_id: StationId;
  readonly end_station_id: StationId;
  readonly sections: SectionId[];
}

export interface RailwayNetwork {
  readonly stations: Station[];
  readonly sections: TrackSection[];
  readonly corridors: Corridor[];
  readonly assets: RailwayAsset[];
}
""",
    "infrastructure/index.ts": """export * from './asset';
export * from './track-section';
export * from './corridor';
""",
    "maintenance/maintenance-task.ts": """import { TaskId, AssetId, SectionId } from '../common/ids';
import { Criticality, Department } from '../common/enums';
import { TimeInterval, DurationMinutes } from '../common/time';

export type TaskType = 'PREVENTIVE' | 'CORRECTIVE' | 'INSPECTION' | 'EMERGENCY';
export type TaskStatus = 'PENDING' | 'SCHEDULED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';

export interface PriorityBreakdown {
  readonly safety_score: number;
  readonly reliability_score: number;
  readonly efficiency_score: number;
  readonly total_score: number;
}

export interface MaintenanceTask {
  readonly task_id: TaskId;
  readonly asset_id: AssetId;
  readonly section_id: SectionId;
  readonly type: TaskType;
  readonly status: TaskStatus;
  readonly criticality: Criticality;
  readonly department: Department;
  readonly description: string;
  readonly requested_window: TimeInterval;
  readonly duration: DurationMinutes;
  readonly requires_power_block: boolean;
  readonly requires_traffic_block: boolean;
  readonly priority_breakdown?: PriorityBreakdown;
}
""",
    "maintenance/defect.ts": """import { DefectId, AssetId, SectionId, TaskId, ISOTimestamp } from '../common/ids';
import { Criticality, Department } from '../common/enums';
import { Provenance } from '../common/provenance';

export type DefectSeverity = 'MINOR' | 'MODERATE' | 'SEVERE' | 'CRITICAL';
export type DefectStatus = 'DETECTED' | 'ASSESSED' | 'LINKED' | 'RECTIFIED' | 'DEFERRED' | 'CLOSED';
export type DefectSource = 'INSPECTION' | 'AUTOMATED_MONITORING' | 'DRIVER_REPORT' | 'AEF_SCAN' | 'BDMS_IMPORT' | 'USER_REPORT';

export interface Defect {
  readonly defect_id: DefectId;
  readonly asset_id: AssetId;
  readonly section_id: SectionId;
  readonly defect_type: string;
  readonly description: string;
  readonly severity: DefectSeverity;
  readonly criticality: Criticality;
  readonly detected_at: ISOTimestamp;
  readonly detected_by: DefectSource;
  readonly operational_impact: string;
  readonly is_safety_critical: boolean;
  readonly urgency_hours: number;
  readonly status: DefectStatus;
  readonly linked_task_id?: TaskId;
  readonly department: Department;
  readonly provenance: Provenance;
}
""",
    "maintenance/index.ts": """export * from './maintenance-task';
export * from './defect';
""",
    "operations/train.ts": """import { TrainId, StationId, SectionId } from '../common/ids';
import { ScheduledTiming } from '../common/time';

export type TrainType = 'EXPRESS' | 'PASSENGER' | 'FREIGHT' | 'MAINTENANCE';

export interface SectionTiming {
  readonly section_id: SectionId;
  readonly entry_time: ScheduledTiming;
  readonly exit_time: ScheduledTiming;
}

export interface TrainService {
  readonly train_id: TrainId;
  readonly name: string;
  readonly train_number: string;
  readonly type: TrainType;
  readonly origin_station_id: StationId;
  readonly destination_station_id: StationId;
  readonly sections: SectionTiming[];
}

export interface Train {
  readonly service: TrainService;
  readonly max_speed_kmh: number;
  readonly length_m: number;
  readonly weight_t: number;
  readonly priority: number;
}
""",
    "operations/train-path.ts": """import { TrainId, SectionId } from '../common/ids';
import { TimeInterval } from '../common/time';

export interface PathConstraint {
  readonly type: string;
  readonly description: string;
}

export interface PathSegment {
  readonly section_id: SectionId;
  readonly interval: TimeInterval;
  readonly is_conflicted: boolean;
}

export interface TrainPath {
  readonly train_id: TrainId;
  readonly segments: PathSegment[];
  readonly constraints: PathConstraint[];
  readonly is_valid: boolean;
}
""",
    "operations/operational-window.ts": """import { WindowId, SectionId } from '../common/ids';
import { TimeInterval } from '../common/time';

export type WindowAvailability = 'AVAILABLE' | 'OCCUPIED' | 'MAINTENANCE' | 'CLOSED';

export interface OperationalWindow {
  readonly window_id: WindowId;
  readonly section_id: SectionId;
  readonly interval: TimeInterval;
  readonly availability: WindowAvailability;
  readonly max_trains: number;
  readonly currently_assigned_trains: number;
}
""",
    "operations/train-impact.ts": """import { TrainId, BlockId } from '../common/ids';
import { RiskLevel } from '../common/enums';

export type ImpactType = 'DELAY' | 'CANCELLATION' | 'REROUTING' | 'HOLD' | 'PATH_CHANGE';

export interface TrainImpact {
  readonly train_id: TrainId;
  readonly block_id: BlockId;
  readonly impact_type: ImpactType;
  readonly delay_minutes: number;
  readonly is_rerouted: boolean;
  readonly is_cancelled: boolean;
  readonly reroute_description?: string;
  readonly severity: RiskLevel;
  readonly reason: string;
  readonly cascading_delay_minutes: number;
}
""",
    "operations/index.ts": """export * from './train';
export * from './train-path';
export * from './operational-window';
export * from './train-impact';
""",
    "planning/block.ts": """import { BlockId, SectionId, TaskId } from '../common/ids';
import { TimeInterval } from '../common/time';

export type BlockStatus = 'DRAFT' | 'REQUESTED' | 'APPROVED' | 'ACTIVE' | 'COMPLETED' | 'CANCELLED';

export interface CandidateBlockWindow {
  readonly interval: TimeInterval;
  readonly suitability_score: number;
  readonly conflicts: string[];
}

export interface Block {
  readonly block_id: BlockId;
  readonly section_id: SectionId;
  readonly interval: TimeInterval;
  readonly status: BlockStatus;
  readonly tasks: TaskId[];
  readonly required_power_off: boolean;
  readonly is_integrated: boolean;
}
""",
    "planning/constraint.ts": """export interface HardConstraint {
  readonly id: string;
  readonly name: string;
  readonly description: string;
}

export interface SoftConstraint {
  readonly id: string;
  readonly name: string;
  readonly description: string;
  readonly weight: number;
}

export interface ConstraintResult {
  readonly constraint_id: string;
  readonly is_satisfied: boolean;
  readonly violation_degree?: number;
  readonly description: string;
}
""",
    "planning/plan.ts": """import { PlanId, ISOTimestamp } from '../common/ids';
import { TimeInterval } from '../common/time';
import { Block } from './block';
import { PlanMetrics } from './plan-metrics';
import { Provenance } from '../common/provenance';

export type PlanStatus = 'DRAFT' | 'PROPOSED' | 'APPROVED' | 'ACTIVE' | 'ARCHIVED' | 'REJECTED';
export type PlanStrategy = 'MAINTENANCE_MAXIMIZED' | 'OPERATIONS_MAXIMIZED' | 'BALANCED';

export interface PlanVersion {
  readonly version: number;
  readonly created_at: ISOTimestamp;
  readonly author: string;
  readonly changes_summary: string;
}

export interface Plan {
  readonly plan_id: PlanId;
  readonly name: string;
  readonly horizon: TimeInterval;
  readonly status: PlanStatus;
  readonly strategy: PlanStrategy;
  readonly blocks: Block[];
  readonly metrics: PlanMetrics;
  readonly version: PlanVersion;
  readonly provenance: Provenance;
}
""",
    "planning/plan-metrics.ts": """export interface ObjectiveTerm {
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
""",
    "planning/index.ts": """export * from './block';
export * from './constraint';
export * from './plan';
export * from './plan-metrics';
""",
    "simulation/scenario.ts": """import { ScenarioId, PlanId, DisruptionId } from '../common/ids';

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
""",
    "simulation/simulation-run.ts": """import { SimulationRunId, ScenarioId, ISOTimestamp } from '../common/ids';
import { TimeInterval } from '../common/time';
import { SimulationResult } from './simulation-result';

export type SimulationStatus = 'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';

export interface SimulationRun {
  readonly run_id: SimulationRunId;
  readonly scenario_id: ScenarioId;
  readonly status: SimulationStatus;
  readonly requested_at: ISOTimestamp;
  readonly completed_at?: ISOTimestamp;
  readonly simulated_horizon: TimeInterval;
  readonly progress_percent: number;
  readonly error_message?: string;
  readonly result?: SimulationResult;
}
""",
    "simulation/simulation-result.ts": """export interface SimulationMetric {
  readonly name: string;
  readonly value: number;
  readonly unit: string;
}

export interface MonteCarloSummary {
  readonly p50: number;
  readonly p90: number;
  readonly p99: number;
  readonly samples: number;
}

export interface SimulationResult {
  readonly is_feasible: boolean;
  readonly total_delay_minutes: number;
  readonly total_delay_p90_minutes?: number;
  readonly cancelled_trains: number;
  readonly delayed_trains: number;
  readonly bottleneck_sections: string[];
  readonly constraint_violations: string[];
  readonly metrics: SimulationMetric[];
  readonly delay_distribution?: MonteCarloSummary;
}
""",
    "simulation/index.ts": """export * from './scenario';
export * from './simulation-run';
export * from './simulation-result';
""",
    "disruption/disruption.ts": """import { DisruptionId, SectionId, ISOTimestamp } from '../common/ids';
import { Criticality } from '../common/enums';
import { TimeInterval } from '../common/time';

export type DisruptionType = 'ASSET_FAILURE' | 'WEATHER' | 'CREW_SHORTAGE' | 'POWER_OUTAGE' | 'ACCIDENT' | 'OTHER';
export type IncidentStatus = 'REPORTED' | 'VERIFIED' | 'UNDER_REPAIR' | 'RESOLVED' | 'CLOSED';

export interface Disruption {
  readonly disruption_id: DisruptionId;
  readonly type: DisruptionType;
  readonly description: string;
  readonly section_id: SectionId;
  readonly estimated_duration: TimeInterval;
  readonly actual_duration?: TimeInterval;
  readonly status: IncidentStatus;
  readonly criticality: Criticality;
  readonly reported_at: ISOTimestamp;
  readonly resolved_at?: ISOTimestamp;
}
""",
    "disruption/recovery.ts": """import { RecoveryPlanId, DisruptionId, BlockId, TaskId, TrainId, ISOTimestamp } from '../common/ids';
import { Provenance } from '../common/provenance';

export type RecoveryActionType = 
  | 'RESCHEDULE_BLOCK'
  | 'SHORTEN_BLOCK'
  | 'MOVE_BLOCK'
  | 'CANCEL_BLOCK'
  | 'REROUTE_TRAIN'
  | 'DEFER_TASK'
  | 'RESEQUENCE_TASKS';

export interface RecoveryAction {
  readonly action_type: RecoveryActionType;
  readonly target_block_id?: BlockId;
  readonly target_task_id?: TaskId;
  readonly target_train_id?: TrainId;
  readonly description: string;
  readonly estimated_delay_reduction_min: number;
}

export type RecoveryStatus = 'PROPOSED' | 'EVALUATING' | 'APPROVED' | 'EXECUTING' | 'COMPLETED' | 'REJECTED';

export interface RecoveryPlan {
  readonly recovery_plan_id: RecoveryPlanId;
  readonly disruption_id: DisruptionId;
  readonly actions: RecoveryAction[];
  readonly status: RecoveryStatus;
  readonly generated_at: ISOTimestamp;
  readonly provenance: Provenance;
}

export interface RecoveryCandidate {
  readonly candidate_id: string;
  readonly recovery_plan_id: RecoveryPlanId;
  readonly estimated_recovery_time_min: number;
  readonly confidence: number;
  readonly trade_offs: string[];
}
""",
    "disruption/index.ts": """export * from './disruption';
export * from './recovery';
""",
    "decision/recommendation.ts": """import { RecommendationId, PlanId, ISOTimestamp } from '../common/ids';
import { PlanMetrics } from '../planning/plan-metrics';

export interface EvidenceItem {
  readonly source: string;
  readonly description: string;
  readonly confidence: number;
}

export interface ConstraintTraceItem {
  readonly constraint_id: string;
  readonly description: string;
  readonly is_satisfied: boolean;
}

export interface RecommendationAlternative {
  readonly alternative_id: string;
  readonly plan_id: PlanId;
  readonly description: string;
  readonly metrics: PlanMetrics;
  readonly trade_offs: string[];
}

export interface Recommendation {
  readonly recommendation_id: RecommendationId;
  readonly target_plan_id: PlanId;
  readonly title: string;
  readonly rationale: string;
  readonly generated_at: ISOTimestamp;
  readonly evidence: EvidenceItem[];
  readonly constraint_traces: ConstraintTraceItem[];
  readonly alternatives: RecommendationAlternative[];
}
""",
    "decision/decision.ts": """import { DecisionId, RecommendationId, ISOTimestamp } from '../common/ids';

export type DecisionStatus = 'PENDING' | 'APPROVED' | 'REJECTED' | 'SUPERSEDED';

export interface Approval {
  readonly approver: string;
  readonly role: string;
  readonly timestamp: ISOTimestamp;
  readonly comments?: string;
}

export interface Decision {
  readonly decision_id: DecisionId;
  readonly recommendation_id: RecommendationId;
  readonly status: DecisionStatus;
  readonly action_taken: string;
  readonly approvals: Approval[];
  readonly recorded_at: ISOTimestamp;
  readonly justification?: string;
}
""",
    "decision/index.ts": """export * from './recommendation';
export * from './decision';
""",
    "events/domain-events.ts": """import { EventId, ISOTimestamp } from '../common/ids';
import { Provenance } from '../common/provenance';

export interface EventEnvelope<T> {
  readonly event_id: EventId;
  readonly event_type: string;
  readonly timestamp: ISOTimestamp;
  readonly provenance: Provenance;
  readonly payload: T;
}

export interface BlockApprovedEvent {
  readonly block_id: string;
  readonly approved_by: string;
}

export interface DisruptionReportedEvent {
  readonly disruption_id: string;
  readonly section_id: string;
  readonly severity: string;
}
""",
    "events/commands.ts": """import { ISOTimestamp } from '../common/ids';

export interface Command<T> {
  readonly command_id: string;
  readonly command_type: string;
  readonly requested_at: ISOTimestamp;
  readonly requested_by: string;
  readonly payload: T;
}
""",
    "events/queries.ts": """import { ISOTimestamp } from '../common/ids';

export interface Query<T> {
  readonly query_id: string;
  readonly query_type: string;
  readonly requested_at: ISOTimestamp;
  readonly params: T;
}
""",
    "events/index.ts": """export * from './domain-events';
export * from './commands';
export * from './queries';
""",
    "ai/predictions.ts": """import { ISOTimestamp } from '../common/ids';
import { Provenance } from '../common/provenance';

export interface PredictionBase {
  readonly model_id: string;
  readonly model_version: string;
  readonly confidence: number;
  readonly generated_at: ISOTimestamp;
  readonly provenance: Provenance;
}

export interface PriorityPrediction extends PredictionBase {
  readonly task_id: string;
  readonly predicted_priority_score: number;
  readonly contributing_factors: Record<string, number>;
}

export interface DurationPrediction extends PredictionBase {
  readonly task_id: string;
  readonly predicted_duration_minutes: number;
  readonly p10_minutes: number;
  readonly p90_minutes: number;
}

export interface DelayPrediction extends PredictionBase {
  readonly train_id: string;
  readonly section_id: string;
  readonly predicted_delay_minutes: number;
}

export interface FailureRiskPrediction extends PredictionBase {
  readonly asset_id: string;
  readonly probability_of_failure: number;
  readonly time_horizon_hours: number;
}
""",
    "ai/index.ts": """export * from './predictions';
""",
    "validation/time.ts": """import { TimeInterval, DurationMinutes } from '../common/time';
import { DomainError, ERROR_CODES } from '../common/errors';
import { makeTimestamp } from '../common/ids';

export function validateTimeInterval(interval: TimeInterval): DomainError | null {
  const startMs = new Date(interval.start).getTime();
  const endMs = new Date(interval.end).getTime();
  if (isNaN(startMs) || isNaN(endMs)) {
    return { code: ERROR_CODES.INVALID_TIME_INTERVAL, message: 'Invalid timestamp', category: 'VALIDATION', severity: 'ERROR', timestamp: makeTimestamp(new Date().toISOString()) };
  }
  if (startMs >= endMs) {
    return { code: ERROR_CODES.INVALID_TIME_INTERVAL, message: 'start must be before end', category: 'VALIDATION', severity: 'ERROR', timestamp: makeTimestamp(new Date().toISOString()) };
  }
  return null;
}

export function validateDuration(duration: DurationMinutes): DomainError | null {
  if (duration.expected <= 0 || duration.minimum <= 0) {
    return { code: ERROR_CODES.INVALID_DURATION, message: 'Duration must be positive', category: 'VALIDATION', severity: 'ERROR', timestamp: makeTimestamp(new Date().toISOString()) };
  }
  if (duration.minimum > duration.maximum) {
    return { code: ERROR_CODES.INVALID_DURATION, message: 'minimum must be <= maximum', category: 'VALIDATION', severity: 'ERROR', timestamp: makeTimestamp(new Date().toISOString()) };
  }
  return null;
}
""",
    "validation/ids.ts": """import { DomainError, ERROR_CODES } from '../common/errors';
import { makeTimestamp } from '../common/ids';

export function validateId(id: string, prefix: string): DomainError | null {
  if (!id || id.trim() === '') {
    return { code: ERROR_CODES.MISSING_REQUIRED_ID, message: `ID cannot be empty for ${prefix}`, category: 'VALIDATION', severity: 'ERROR', timestamp: makeTimestamp(new Date().toISOString()) };
  }
  return null;
}
""",
    "validation/index.ts": """export * from './time';
export * from './ids';
""",
    "index.ts": """export * from './common';
export * from './infrastructure';
export * from './maintenance';
export * from './operations';
export * from './planning';
export * from './simulation';
export * from './disruption';
export * from './decision';
export * from './events';
export * from './ai';
export * from './validation';
"""
}

for path, content in files.items():
    full_path = os.path.join(base, path)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Created all files.")
