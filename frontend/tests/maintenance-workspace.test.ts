import { describe, it, expect } from 'vitest';
import {
  computeDueState,
  matchesMaintenanceFilter,
  sortMaintenanceTasks,
  type MaintenanceFilters,
} from '../hooks/useMaintenanceWorkspace';
import { deriveCommandCenterAlerts } from '../hooks/deriveCommandCenterAlerts';
import type { MaintenanceTask } from '../domain';

const BASE_FILTERS: MaintenanceFilters = {
  status: 'ALL',
  priority: 'ALL',
  type: 'ALL',
  sectionId: '',
  assetId: '',
  dueState: 'ALL',
  searchQuery: '',
  sort: 'priority-desc',
};

function makeTask(overrides: Partial<MaintenanceTask> = {}): MaintenanceTask {
  return {
    task_id: 'TSK-TEST-01',
    title: 'Test turnout tamping',
    section_id: 'SEC-04',
    asset_id: 'AST-TRK-01',
    department: 'Engineering',
    task_type: 'Defect',
    expected_duration_min: 180,
    duration_estimates: { expected_min: 180, p10_min: 150, p90_min: 240, overrun_probability: 0.28, confidence: 0.91 },
    crew_size_required: 8,
    crew_qualification: 'Engineering',
    criticality: 'CRITICAL',
    overdue_days: 3,
    dependency_task_ids: [],
    earliest_start: '2026-09-08T02:00:00Z',
    latest_finish: '2026-09-08T08:00:00Z',
    priority_score: 94.5,
    status: 'Pending',
    ...overrides,
  };
}

describe('computeDueState', () => {
  it('marks overdue tasks as Overdue', () => {
    expect(computeDueState(makeTask({ overdue_days: 5 }))).toBe('Overdue');
  });

  it('returns No Deadline when latest_finish is missing', () => {
    expect(computeDueState(makeTask({ overdue_days: 0, latest_finish: undefined }))).toBe('No Deadline');
  });

  it('marks past-due latest_finish as Overdue', () => {
    expect(computeDueState(makeTask({ overdue_days: 0, latest_finish: '2020-01-01T00:00:00Z' }))).toBe('Overdue');
  });

  it('marks far-future latest_finish as Upcoming', () => {
    expect(computeDueState(makeTask({ overdue_days: 0, latest_finish: '2099-01-01T00:00:00Z' }))).toBe('Upcoming');
  });
});

describe('matchesMaintenanceFilter', () => {
  const task = makeTask();

  it('passes with default ALL filters', () => {
    expect(matchesMaintenanceFilter(task, BASE_FILTERS)).toBe(true);
  });

  it('filters by status', () => {
    expect(matchesMaintenanceFilter(task, { ...BASE_FILTERS, status: 'Pending' })).toBe(true);
    expect(matchesMaintenanceFilter(task, { ...BASE_FILTERS, status: 'Completed' })).toBe(false);
  });

  it('filters by priority (criticality)', () => {
    expect(matchesMaintenanceFilter(task, { ...BASE_FILTERS, priority: 'CRITICAL' })).toBe(true);
    expect(matchesMaintenanceFilter(task, { ...BASE_FILTERS, priority: 'LOW' })).toBe(false);
  });

  it('filters by maintenance type', () => {
    expect(matchesMaintenanceFilter(task, { ...BASE_FILTERS, type: 'Defect' })).toBe(true);
    expect(matchesMaintenanceFilter(task, { ...BASE_FILTERS, type: 'Preventive' })).toBe(false);
  });

  it('filters by section and asset', () => {
    expect(matchesMaintenanceFilter(task, { ...BASE_FILTERS, sectionId: 'SEC-04' })).toBe(true);
    expect(matchesMaintenanceFilter(task, { ...BASE_FILTERS, sectionId: 'SEC-99' })).toBe(false);
    expect(matchesMaintenanceFilter(task, { ...BASE_FILTERS, assetId: 'AST-TRK-01' })).toBe(true);
    expect(matchesMaintenanceFilter(task, { ...BASE_FILTERS, assetId: 'AST-OTHER' })).toBe(false);
  });

  it('filters by due state', () => {
    expect(matchesMaintenanceFilter(task, { ...BASE_FILTERS, dueState: 'Overdue' })).toBe(true);
    expect(matchesMaintenanceFilter(task, { ...BASE_FILTERS, dueState: 'Upcoming' })).toBe(false);
  });

  it('searches across task id, title, section, asset, type', () => {
    expect(matchesMaintenanceFilter(task, { ...BASE_FILTERS, searchQuery: 'tsk-test-01' })).toBe(true);
    expect(matchesMaintenanceFilter(task, { ...BASE_FILTERS, searchQuery: 'tamping' })).toBe(true);
    expect(matchesMaintenanceFilter(task, { ...BASE_FILTERS, searchQuery: 'sec-04' })).toBe(true);
    expect(matchesMaintenanceFilter(task, { ...BASE_FILTERS, searchQuery: 'ast-trk' })).toBe(true);
    expect(matchesMaintenanceFilter(task, { ...BASE_FILTERS, searchQuery: 'no-such-thing-xyz' })).toBe(false);
  });

  it('combines multiple filters (AND semantics)', () => {
    expect(
      matchesMaintenanceFilter(task, { ...BASE_FILTERS, status: 'Pending', priority: 'CRITICAL', sectionId: 'SEC-04' }),
    ).toBe(true);
    expect(
      matchesMaintenanceFilter(task, { ...BASE_FILTERS, status: 'Pending', priority: 'LOW' }),
    ).toBe(false);
  });
});

describe('sortMaintenanceTasks', () => {
  const critical = makeTask({ task_id: 'TSK-A', criticality: 'CRITICAL', priority_score: 94.5, overdue_days: 3, latest_finish: '2026-09-08T08:00:00Z' });
  const high = makeTask({ task_id: 'TSK-B', criticality: 'HIGH', priority_score: 88.0, overdue_days: 7, latest_finish: '2026-09-07T08:00:00Z' });
  const medium = makeTask({ task_id: 'TSK-C', criticality: 'MEDIUM', priority_score: 65.0, overdue_days: 0, latest_finish: undefined });

  it('orders criticality first on priority-desc (operational attention default)', () => {
    const sorted = sortMaintenanceTasks([medium, high, critical], 'priority-desc');
    expect(sorted.map((t) => t.task_id)).toEqual(['TSK-A', 'TSK-B', 'TSK-C']);
  });

  it('reverses criticality on priority-asc', () => {
    const sorted = sortMaintenanceTasks([critical, high, medium], 'priority-asc');
    expect(sorted.map((t) => t.task_id)).toEqual(['TSK-C', 'TSK-B', 'TSK-A']);
  });

  it('orders most-overdue first on overdue-desc', () => {
    const sorted = sortMaintenanceTasks([medium, critical, high], 'overdue-desc');
    expect(sorted.map((t) => t.task_id)).toEqual(['TSK-B', 'TSK-A', 'TSK-C']);
  });

  it('orders task ids alphabetically', () => {
    const sorted = sortMaintenanceTasks([high, critical, medium], 'task-id-asc');
    expect(sorted.map((t) => t.task_id)).toEqual(['TSK-A', 'TSK-B', 'TSK-C']);
  });

  it('does not mutate the input array', () => {
    const input = [medium, high, critical];
    sortMaintenanceTasks(input, 'priority-desc');
    expect(input.map((t) => t.task_id)).toEqual(['TSK-C', 'TSK-B', 'TSK-A']);
  });
});

describe('maintenance alerts derivation (no fabricated facts)', () => {
  it('creates overdue alerts only for actually overdue tasks', () => {
    const alerts = deriveCommandCenterAlerts({
      tasks: [makeTask({ overdue_days: 3 }), makeTask({ task_id: 'TSK-OK', overdue_days: 0, latest_finish: undefined })],
      defects: [],
      incidents: [],
      trains: [],
      plans: [],
      decisions: [],
      recommendation: null,
      backendHealthy: true,
    });
    const overdue = alerts.filter((a) => a.id.startsWith('task-overdue:'));
    expect(overdue).toHaveLength(1);
    expect(overdue[0]?.id).toBe('task-overdue:TSK-TEST-01');
  });

  it('does not invent train delays from task existence', () => {
    const alerts = deriveCommandCenterAlerts({
      tasks: [makeTask()],
      defects: [],
      incidents: [],
      trains: [
        {
          train_id: 'TRN-1', train_number: '12001', name: 'Test', train_type: 'Passenger', priority: 1,
          origin_station_id: 'STN-A', destination_station_id: 'STN-F', route_section_ids: ['SEC-04'],
          schedule: [], current_status: 'ON_TIME', current_delay_min: 0, cascading_delay_estimate_min: 0,
        },
      ],
      plans: [],
      decisions: [],
      recommendation: null,
      backendHealthy: true,
    });
    expect(alerts.filter((a) => a.id === 'trains:delays')).toHaveLength(0);
  });
});
