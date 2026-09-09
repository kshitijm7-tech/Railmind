/**
 * F01 — Backend contract -> frontend domain mapping.
 *
 * Canonical wire types live in frontend/contracts (source of truth).
 * UI view models live in frontend/domain. This module is the ONLY place
 * that translates between them, so camelCase/snake_case and enum
 * mismatches are isolated here.
 *
 * Provenance (state/source/version/timestamps) from the backend is attached
 * as `_provenance` / `_source` on mapped objects without changing the
 * domain shapes consumed by the UI.
 */

import type {
  RailwayNetwork as DomainNetwork,
  MaintenanceTask as DomainMaintenanceTask,
  TrainService as DomainTrainService,
  CandidateBlockWindow as DomainCandidateWindow,
  Plan as DomainPlan,
  Block as DomainBlock,
  DecisionRecord as DomainDecision,
} from '../../domain';

// --- Backend wire shapes (minimal, tolerant) ---

interface WireTimeInterval {
  start?: unknown;
  end?: unknown;
}

interface WireDuration {
  expected?: unknown;
  minimum?: unknown;
  maximum?: unknown;
}

interface WireMaintenanceTask {
  task_id?: unknown;
  asset_id?: unknown;
  section_id?: unknown;
  type?: unknown;
  status?: unknown;
  criticality?: unknown;
  department?: unknown;
  description?: unknown;
  requested_window?: WireTimeInterval | null;
  duration?: WireDuration | null;
  requires_power_block?: unknown;
  requires_traffic_block?: unknown;
  priority_breakdown?: { total_score?: unknown } | null;
  provenance?: WireProvenance | null;
}

interface WireDefect {
  defect_id?: unknown;
  asset_id?: unknown;
  section_id?: unknown;
  defect_type?: unknown;
  description?: unknown;
  severity?: unknown;
  criticality?: unknown;
  detected_at?: unknown;
  operational_impact?: unknown;
  status?: unknown;
  department?: unknown;
}

interface WireProvenance {
  state?: unknown;
  source?: unknown;
  generatedAt?: unknown;
  generatorVersion?: unknown;
}

interface WireTrainSection {
  section_id?: unknown;
  entry_time?: { scheduled?: unknown; delayMinutes?: unknown };
  exit_time?: { scheduled?: unknown; delayMinutes?: unknown };
}

interface WireTrain {
  service?: {
    train_id?: unknown;
    name?: unknown;
    train_number?: unknown;
    type?: unknown;
    origin_station_id?: unknown;
    destination_station_id?: unknown;
    sections?: WireTrainSection[] | null;
  } | null;
  priority?: unknown;
}

interface WireAsset {
  asset_id?: unknown;
  category?: unknown;
  name?: unknown;
  location_section?: unknown;
  location_station?: unknown;
  criticality?: unknown;
  is_operational?: unknown;
}

interface WireTrackSection {
  section_id?: unknown;
  name?: unknown;
  start_station_id?: unknown;
  end_station_id?: unknown;
  length_km?: unknown;
  max_speed_kmh?: unknown;
  track_count?: unknown;
}

interface WireStation {
  station_id?: unknown;
  code?: unknown;
  name?: unknown;
  sequence?: unknown;
  km?: unknown;
  category?: unknown;
  platforms?: unknown;
  loop_lines?: unknown;
  is_junction?: unknown;
}

interface WireCorridor {
  corridor_id?: unknown;
  name?: unknown;
  start_station_id?: unknown;
  end_station_id?: unknown;
  sections?: unknown;
}

interface WirePlan {
  plan_id?: unknown;
  name?: unknown;
  horizon?: unknown;
  status?: unknown;
  strategy?: unknown;
  blocks?: WireBlock[] | null;
  metrics?: {
    total_maintenance_time_minutes?: unknown;
    total_train_delay_minutes?: unknown;
    constraints_violated?: unknown;
    resource_utilization_percent?: unknown;
    overall_score?: unknown;
  } | null;
  version?: { version?: unknown; created_at?: unknown } | null;
  provenance?: WireProvenance | null;
}

interface WireBlock {
  block_id?: unknown;
  section_id?: unknown;
  interval?: WireTimeInterval | null;
  status?: unknown;
  tasks?: unknown;
  required_power_off?: unknown;
  is_integrated?: unknown;
}

interface WireDecision {
  decision_id?: unknown;
  recommendation_id?: unknown;
  target_plan_id?: unknown;
  target_plan_version?: unknown;
  status?: unknown;
  action_taken?: unknown;
  approvals?: Array<{ approver?: unknown; role?: unknown; comments?: unknown }> | null;
  recorded_at?: unknown;
  justification?: unknown;
}

interface WireAsyncJob {
  jobId?: unknown;
  status?: unknown;
  requestedAt?: unknown;
  startedAt?: unknown;
  completedAt?: unknown;
  progressPercent?: unknown;
  resultEndpoint?: unknown;
  errorCode?: unknown;
  errorMessage?: unknown;
}

// --- Small guards ---

function asString(value: unknown, fallback = ''): string {
  return typeof value === 'string' ? value : fallback;
}

function asNumber(value: unknown, fallback = 0): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback;
}

function asStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((v): v is string => typeof v === 'string') : [];
}

function asIsoString(value: unknown, fallback: string): string {
  if (typeof value === 'string' && value.length > 0) return value;
  return fallback;
}

export function tagProvenance<T extends object>(obj: T, provenance: unknown, source: 'REAL' | 'MOCK'): T {
  try {
    Object.defineProperty(obj, '_provenance', { value: provenance ?? null, enumerable: false, writable: true });
    Object.defineProperty(obj, '_source', { value: source, enumerable: false, writable: true });
  } catch {
    // Non-critical: provenance is advisory only.
  }
  return obj;
}

// --- Maintenance ---

const TASK_TYPE_MAP: Record<string, DomainMaintenanceTask['task_type']> = {
  PREVENTIVE: 'Preventive',
  CORRECTIVE: 'Corrective',
  INSPECTION: 'Inspection',
  EMERGENCY: 'Defect',
  REPAIR: 'Corrective',
  REPLACEMENT: 'Corrective',
};

const TASK_STATUS_MAP: Record<string, DomainMaintenanceTask['status']> = {
  PENDING: 'Pending',
  SCHEDULED: 'Scheduled',
  IN_PROGRESS: 'In Progress',
  COMPLETED: 'Completed',
  CANCELLED: 'Cancelled',
};

export function mapMaintenanceTask(wire: unknown): DomainMaintenanceTask {
  const w = (wire ?? {}) as WireMaintenanceTask;
  const taskId = asString(w.task_id);
  const description = asString(w.description, taskId || 'Maintenance task');
  const durationExpected = asNumber(w.duration?.expected, 60);
  const durationMin = asNumber(w.duration?.minimum, Math.max(15, durationExpected - 15));
  const durationMax = asNumber(w.duration?.maximum, durationExpected + 30);
  const priorityScore = asNumber(w.priority_breakdown?.total_score, 50);
  const requestedStart = typeof w.requested_window?.start === 'string' ? w.requested_window.start : undefined;
  const nowIso = new Date().toISOString();

  const mapped: DomainMaintenanceTask = {
    task_id: taskId,
    title: description,
    section_id: asString(w.section_id, 'SEC-UNKNOWN'),
    asset_id: typeof w.asset_id === 'string' ? w.asset_id : undefined,
    department: (typeof w.department === 'string' ? w.department : 'Engineering') as DomainMaintenanceTask['department'],
    task_type: TASK_TYPE_MAP[asString(w.type, 'PREVENTIVE')] ?? 'Preventive',
    expected_duration_min: durationExpected,
    duration_estimates: {
      expected_min: durationExpected,
      p10_min: durationMin,
      p90_min: durationMax,
      // Derived view-model default (documented): backend exposes only
      // min/expected/max, not a calibrated overrun probability.
      overrun_probability: durationMax > durationExpected ? 0.15 : 0.05,
      confidence: 0.8,
    },
    crew_size_required: 4,
    crew_qualification: (typeof w.department === 'string' ? w.department : 'Engineering') as DomainMaintenanceTask['department'],
    criticality: (typeof w.criticality === 'string' ? w.criticality : 'MEDIUM') as DomainMaintenanceTask['criticality'],
    overdue_days: 0,
    dependency_task_ids: [],
    earliest_start: requestedStart ?? nowIso,
    priority_score: priorityScore,
    status: TASK_STATUS_MAP[asString(w.status, 'PENDING')] ?? 'Pending',
  };
  return tagProvenance(mapped, w.provenance ?? null, 'REAL');
}

export function mapDefectToIncident(wire: unknown): import('../../domain').Incident {
  const w = (wire ?? {}) as WireDefect;
  const defectId = asString(w.defect_id, `DEF-${Date.now()}`);
  const description = asString(w.description, defectId);
  const impact = asString(w.operational_impact);
  return tagProvenance(
    {
      incident_id: defectId,
      incident_type: 'TRACK_UNAVAILABLE',
      title: description,
      section_id: asString(w.section_id, 'SEC-UNKNOWN'),
      severity: (typeof w.criticality === 'string' ? w.criticality : 'MEDIUM') as import('../../domain').Incident['severity'],
      status: 'Detected',
      detected_at: asIsoString(w.detected_at, new Date().toISOString()),
      estimated_resolution_time: new Date(Date.now() + 4 * 3600 * 1000).toISOString(),
      affected_plan_id: undefined,
      affected_train_ids: [],
      affected_block_ids: [],
      description: impact ? `${description} — ${impact}` : description,
    },
    null,
    'REAL',
  );
}

// --- Trains ---

const TRAIN_TYPE_MAP: Record<string, DomainTrainService['train_type']> = {
  EXPRESS: 'Passenger',
  PASSENGER: 'Passenger',
  FREIGHT: 'Goods',
  GOODS: 'Goods',
  MAINTENANCE: 'Special',
  SPECIAL: 'Special',
};

export function mapTrain(wire: unknown): DomainTrainService {
  const w = (wire ?? {}) as WireTrain;
  const service = w.service ?? {};
  const trainId = asString(service.train_id, 'TRN-UNKNOWN');
  const sections = Array.isArray(service.sections) ? service.sections : [];
  let maxDelay = 0;
  const schedule = sections.map((s) => {
    const entryScheduled = asIsoString(s.entry_time?.scheduled, new Date().toISOString());
    const exitScheduled = asIsoString(s.exit_time?.scheduled, entryScheduled);
    const delay = Math.max(asNumber(s.entry_time?.delayMinutes, 0), asNumber(s.exit_time?.delayMinutes, 0));
    if (delay > maxDelay) maxDelay = delay;
    return {
      section_id: asString(s.section_id, 'SEC-UNKNOWN'),
      scheduled_entry: entryScheduled,
      scheduled_exit: exitScheduled,
      delay_minutes: delay,
    };
  });

  const mapped: DomainTrainService = {
    train_id: trainId,
    train_number: asString(service.train_number, trainId),
    name: asString(service.name, trainId),
    train_type: TRAIN_TYPE_MAP[asString(service.type, 'PASSENGER')] ?? 'Passenger',
    priority: asNumber(w.priority, 3),
    origin_station_id: asString(service.origin_station_id, 'STN-UNKNOWN'),
    destination_station_id: asString(service.destination_station_id, 'STN-UNKNOWN'),
    route_section_ids: schedule.map((s) => s.section_id),
    schedule,
    current_status: maxDelay > 0 ? 'DELAYED' : 'ON_TIME',
    current_delay_min: maxDelay,
    cascading_delay_estimate_min: 0,
  };
  return tagProvenance(mapped, null, 'REAL');
}

// --- Infrastructure / network ---

export function mapNetwork(
  assets: unknown,
  sections: unknown,
  corridors: unknown,
  stations?: unknown,
): DomainNetwork {
  const wireAssets = (Array.isArray(assets) ? assets : []) as WireAsset[];
  const wireSections = (Array.isArray(sections) ? sections : []) as WireTrackSection[];
  const wireCorridors = (Array.isArray(corridors) ? corridors : []) as WireCorridor[];
  const wireStations = (Array.isArray(stations) ? stations : []) as WireStation[];

  const corridor = wireCorridors[0];
  const stationIds = new Set<string>();
  for (const s of wireSections) {
    if (typeof s.start_station_id === 'string') stationIds.add(s.start_station_id);
    if (typeof s.end_station_id === 'string') stationIds.add(s.end_station_id);
  }
  if (typeof corridor?.start_station_id === 'string') stationIds.add(corridor.start_station_id);
  if (typeof corridor?.end_station_id === 'string') stationIds.add(corridor.end_station_id);

  // Canonical station registry when the backend provides it
  // (GET /stations); otherwise synthesize stable placeholders so the
  // existing UI contract holds.
  const registry = new Map<string, WireStation>();
  for (const st of wireStations) {
    if (typeof st.station_id === 'string') registry.set(st.station_id, st);
  }
  const orderedStations = [...stationIds].sort();
  if (registry.size > 0) {
    const ranked = [...registry.values()]
      .filter((st) => typeof st.station_id === 'string')
      .sort((a, b) => asNumber(a.sequence, 0) - asNumber(b.sequence, 0));
    for (const st of ranked) {
      if (!stationIds.has(asString(st.station_id))) orderedStations.push(asString(st.station_id));
    }
  }

  return {
    zone: 'RailMind Division',
    division: 'Central Division',
    corridor: asString(corridor?.name, 'Operational Corridor'),
    stations: orderedStations.map((id) => {
      const reg = registry.get(id);
      if (reg) {
        const platforms = asNumber(reg.platforms, 2);
        return {
          station_id: id,
          name: asString(reg.name, id),
          code: asString(reg.code, id.slice(0, 4).toUpperCase()),
          platforms,
          tracks: platforms + asNumber(reg.loop_lines, 0),
          is_junction: reg.is_junction === true,
        };
      }
      return {
        station_id: id,
        name: id,
        code: id.slice(0, 4).toUpperCase(),
        platforms: 2,
        tracks: 2,
        is_junction: false,
      };
    }),
    sections: wireSections.map((s) => ({
      section_id: asString(s.section_id, 'SEC-UNKNOWN'),
      name: asString(s.name, asString(s.section_id, 'Section')),
      from_station_id: asString(s.start_station_id, 'STN-UNKNOWN'),
      to_station_id: asString(s.end_station_id, 'STN-UNKNOWN'),
      length_km: asNumber(s.length_km, 0),
      track_count: asNumber(s.track_count, 1),
      max_speed_kmph: asNumber(s.max_speed_kmh, 100),
      department_owners: ['Engineering'],
      criticality: 'MEDIUM',
      status: 'OPERATIONAL',
    })),
    assets: wireAssets.map((a) => ({
      asset_id: asString(a.asset_id, 'AST-UNKNOWN'),
      asset_type: 'TrackAsset',
      name: asString(a.name, asString(a.asset_id, 'Asset')),
      section_id: asString(a.location_section, 'SEC-UNKNOWN'),
      department: 'Engineering',
      health_score: a.is_operational === false ? 40 : 85,
      criticality: (typeof a.criticality === 'string' ? a.criticality : 'MEDIUM') as DomainNetwork['assets'][number]['criticality'],
      last_inspected: new Date().toISOString() as import('../../contracts/common/ids').ISOTimestamp,
      next_due: new Date(Date.now() + 7 * 86400 * 1000).toISOString() as import('../../contracts/common/ids').ISOTimestamp,
      status: a.is_operational === false ? 'DEFECTIVE' : 'HEALTHY',
    })),
  };
}

// --- Planning ---

const PLAN_STATUS_MAP: Record<string, DomainPlan['status']> = {
  DRAFT: 'Draft',
  PROPOSED: 'Generated',
  APPROVED: 'Approved',
  ACTIVE: 'Approved',
  ARCHIVED: 'Superseded',
  REJECTED: 'Rejected',
};

const PLAN_STRATEGY_MAP: Record<string, DomainPlan['strategy']> = {
  BALANCED: 'Balanced',
  MAINTENANCE_MAXIMIZED: 'Maintenance Priority',
  OPERATIONS_MAXIMIZED: 'Operations Priority',
};

const BLOCK_STATUS_MAP: Record<string, DomainBlock['status']> = {
  DRAFT: 'Requested',
  REQUESTED: 'Requested',
  APPROVED: 'Approved',
  ACTIVE: 'Active',
  COMPLETED: 'Completed',
  CANCELLED: 'Cancelled',
};

export function mapBlock(wire: unknown, planVersion: number): DomainBlock {
  const w = (wire ?? {}) as WireBlock;
  const start = asIsoString(w.interval?.start, new Date().toISOString());
  const end = asIsoString(w.interval?.end, start);
  const durationMin = Math.max(0, Math.round((Date.parse(end) - Date.parse(start)) / 60000) || 0);
  const tasks = asStringArray(w.tasks);
  return {
    block_id: asString(w.block_id, `BLK-${Date.now()}`),
    section_id: asString(w.section_id, 'SEC-UNKNOWN'),
    start_time: start as import('../../contracts/common/ids').ISOTimestamp,
    end_time: end as import('../../contracts/common/ids').ISOTimestamp,
    duration_min: durationMin,
    assigned_task_ids: tasks,
    departments_involved: [],
    is_bundled: tasks.length > 1 || w.is_integrated === true,
    status: BLOCK_STATUS_MAP[asString(w.status, 'DRAFT')] ?? 'Requested',
    plan_version: planVersion,
    affected_train_ids: [],
  };
}

export function mapPlan(wire: unknown): DomainPlan {
  const w = (wire ?? {}) as WirePlan;
  const version = asNumber(w.version?.version, 1);
  const blocks = Array.isArray(w.blocks) ? w.blocks.map((b) => mapBlock(b, version)) : [];
  const delay = asNumber(w.metrics?.total_train_delay_minutes, 0);
  const score = asNumber(w.metrics?.overall_score, 0);
  const mapped: DomainPlan = {
    plan_id: asString(w.plan_id, `PLAN-${Date.now()}`),
    name: asString(w.name, asString(w.plan_id, 'Generated plan')),
    version,
    state_version: 'LIVE',
    strategy: PLAN_STRATEGY_MAP[asString(w.strategy, 'BALANCED')] ?? 'Balanced',
    status: PLAN_STATUS_MAP[asString(w.status, 'DRAFT')] ?? 'Draft',
    blocks,
    metrics: {
      total_delay_minutes: delay,
      passenger_trains_affected: 0,
      goods_trains_affected: 0,
      maintenance_tasks_completed: blocks.reduce((n, b) => n + b.assigned_task_ids.length, 0),
      maintenance_tasks_unscheduled: 0,
      blocks_count: blocks.length,
      bundled_blocks_count: blocks.filter((b) => b.is_bundled).length,
      overall_overrun_risk: 0.1,
      objective_score: score,
    },
    created_at: asIsoString(w.version?.created_at, new Date().toISOString()) as import('../../contracts/common/ids').ISOTimestamp,
    solver_runtime_ms: 0,
  };
  return tagProvenance(mapped, w.provenance ?? null, 'REAL');
}

export function mapCandidateWindow(wire: unknown, index: number): DomainCandidateWindow {
  const w = (wire ?? {}) as { interval?: WireTimeInterval; conflicts?: unknown; section_id?: unknown };
  const start = asIsoString(w.interval?.start, new Date().toISOString());
  const end = asIsoString(w.interval?.end, start);
  const durationMin = Math.max(0, Math.round((Date.parse(end) - Date.parse(start)) / 60000) || 0);
  return {
    window_id: `WIN-API-${index}`,
    section_id: asString(w.section_id, 'SEC-UNKNOWN'),
    earliest_start: start,
    latest_end: end,
    max_duration_min: durationMin,
    conflicting_train_ids: asStringArray(w.conflicts),
    recommended_usage: 'NIGHT_POSSESSION',
  };
}

// --- Decisions ---

function mapDecisionAction(actionTaken: string, status: string): DomainDecision['action'] {
  const a = `${actionTaken} ${status}`.toUpperCase();
  if (a.includes('REJECT')) return 'REJECT';
  if (a.includes('MODIFY') || a.includes('DEFER') || a.includes('CHANGE')) return 'MODIFY';
  return 'APPROVE';
}

function mapUserRole(role: string): DomainDecision['user_role'] {
  const r = role.toUpperCase();
  if (r.includes('PLAN')) return 'Planning Officer';
  if (r.includes('SENIOR') || r.includes('MANAGER') || r.includes('ADMIN') || r.includes('ENGINEER'))
    return 'Senior Divisional Engineer';
  return 'Operations Controller';
}

export function mapDecision(wire: unknown): DomainDecision {
  const w = (wire ?? {}) as WireDecision;
  const firstApproval = Array.isArray(w.approvals) ? w.approvals[0] : undefined;
  const authorizedBy = asString(firstApproval?.approver, 'RailMind Approver');
  const role = asString(firstApproval?.role, 'OPERATOR');
  return tagProvenance(
    {
      decision_id: asString(w.decision_id, `DEC-${Date.now()}`),
      recommendation_id: asString(w.recommendation_id, 'REC-UNKNOWN'),
      plan_id: asString(w.target_plan_id, 'PLAN-UNKNOWN'),
      state_version: asString(w.target_plan_version, 'LIVE'),
      action: mapDecisionAction(asString(w.action_taken), asString(w.status)),
      authorized_by: authorizedBy,
      user_role: mapUserRole(role),
      timestamp: asIsoString(w.recorded_at, new Date().toISOString()) as import('../../contracts/common/ids').ISOTimestamp,
      notes: typeof w.justification === 'string' ? w.justification : undefined,
    },
    null,
    'REAL',
  );
}

// --- Async jobs (202 Accepted polling shape) ---

const JOB_STATUSES = new Set(['QUEUED', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED']);

export function mapAsyncJob(wire: unknown): import('../../contracts/api/common/job').AsyncJob {
  const w = (wire ?? {}) as WireAsyncJob;
  const status = asString(w.status, 'QUEUED');
  return {
    jobId: asString(w.jobId, `JOB-${Date.now()}`),
    status: (JOB_STATUSES.has(status) ? status : 'QUEUED') as import('../../contracts/api/common/job').JobStatus,
    requestedAt: asIsoString(w.requestedAt, new Date().toISOString()) as import('../../contracts/common/ids').ISOTimestamp,
    startedAt: typeof w.startedAt === 'string' ? (w.startedAt as import('../../contracts/common/ids').ISOTimestamp) : undefined,
    completedAt: typeof w.completedAt === 'string' ? (w.completedAt as import('../../contracts/common/ids').ISOTimestamp) : undefined,
    progressPercent: typeof w.progressPercent === 'number' ? w.progressPercent : undefined,
    resultEndpoint: typeof w.resultEndpoint === 'string' ? w.resultEndpoint : undefined,
    errorCode: typeof w.errorCode === 'string' ? w.errorCode : undefined,
    errorMessage: typeof w.errorMessage === 'string' ? w.errorMessage : undefined,
  };
}
