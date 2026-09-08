import { describe, it, expect } from 'vitest';
import { mapAsyncJob, mapDecision, mapMaintenanceTask, mapNetwork, mapPlan, mapTrain } from '../services/api/mappers';

describe('API mappers (contract -> domain)', () => {
  it('maps a backend maintenance task to the domain view model', () => {
    const task = mapMaintenanceTask({
      task_id: 'TASK-001',
      asset_id: 'AST-101',
      section_id: 'SEC-002',
      type: 'CORRECTIVE',
      status: 'SCHEDULED',
      criticality: 'CRITICAL',
      department: 'S&T',
      description: 'Fix faulty signal head',
      duration: { expected: 60, minimum: 45, maximum: 90 },
      requires_power_block: true,
      requires_traffic_block: true,
      priority_breakdown: { total_score: 23 },
    });
    expect(task.task_id).toBe('TASK-001');
    expect(task.title).toBe('Fix faulty signal head');
    expect(task.task_type).toBe('Corrective');
    expect(task.status).toBe('Scheduled');
    expect(task.expected_duration_min).toBe(60);
    expect(task.duration_estimates.p10_min).toBe(45);
    expect(task.duration_estimates.p90_min).toBe(90);
    expect(task.priority_score).toBe(23);
  });

  it('maps backend Train wrapping (service) to domain TrainService', () => {
    const train = mapTrain({
      service: {
        train_id: 'TRN-500',
        name: 'Rajdhani Express',
        train_number: '12951',
        type: 'EXPRESS',
        origin_station_id: 'ST-1',
        destination_station_id: 'ST-3',
        sections: [
          {
            section_id: 'SEC-001',
            entry_time: { scheduled: '2026-09-08T06:00:00Z', delayMinutes: 0 },
            exit_time: { scheduled: '2026-09-08T06:15:00Z', delayMinutes: 5 },
          },
        ],
      },
      priority: 1,
    });
    expect(train.train_id).toBe('TRN-500');
    expect(train.train_type).toBe('Passenger');
    expect(train.route_section_ids).toEqual(['SEC-001']);
    expect(train.current_delay_min).toBe(5);
    expect(train.current_status).toBe('DELAYED');
  });

  it('composes a network from assets, sections, and corridors', () => {
    const network = mapNetwork(
      [{ asset_id: 'AST-100', name: 'Switch A', location_section: 'SEC-001', criticality: 'HIGH', is_operational: true }],
      [
        {
          section_id: 'SEC-001',
          name: 'Section 1',
          start_station_id: 'ST-1',
          end_station_id: 'ST-2',
          length_km: 15.5,
          max_speed_kmh: 120,
          track_count: 2,
        },
      ],
      [{ corridor_id: 'CORR-01', name: 'North Main Corridor', start_station_id: 'ST-1', end_station_id: 'ST-2', sections: ['SEC-001'] }],
    );
    expect(network.sections).toHaveLength(1);
    expect(network.assets).toHaveLength(1);
    expect(network.stations.map((s) => s.station_id).sort()).toEqual(['ST-1', 'ST-2']);
    expect(network.corridor).toBe('North Main Corridor');
  });

  it('maps a backend plan while preserving provenance metadata', () => {
    const plan = mapPlan({
      plan_id: 'PLAN-001',
      name: 'Weekend Track Overhaul',
      status: 'APPROVED',
      strategy: 'BALANCED',
      blocks: [
        {
          block_id: 'BLK-1',
          section_id: 'SEC-A',
          interval: { start: '2026-09-09T02:00:00Z', end: '2026-09-09T10:00:00Z' },
          status: 'APPROVED',
          tasks: ['TASK-001'],
          required_power_off: false,
          is_integrated: true,
        },
      ],
      metrics: { total_train_delay_minutes: 20.5, overall_score: 95.0 },
      version: { version: 1, created_at: '2026-09-08T01:00:00Z' },
      provenance: { state: 'MOCKED', source: 'SYSTEM', generatedAt: '2026-09-08T01:00:00Z', generatorVersion: 'v1.0.0' },
    });
    expect(plan.plan_id).toBe('PLAN-001');
    expect(plan.status).toBe('Approved');
    expect(plan.strategy).toBe('Balanced');
    expect(plan.blocks).toHaveLength(1);
    expect(plan.blocks[0]?.duration_min).toBe(480);
    expect(plan.metrics.total_delay_minutes).toBe(20.5);
    const provenance = (plan as unknown as { _provenance?: { state?: string } })._provenance;
    expect(provenance?.state).toBe('MOCKED');
  });

  it('maps a backend decision to the domain decision record', () => {
    const decision = mapDecision({
      decision_id: 'DEC-1',
      recommendation_id: 'REC-1',
      target_plan_id: 'PLAN-001',
      target_plan_version: 'v1',
      status: 'APPROVED',
      action_taken: 'APPROVED',
      approvals: [{ approver: 'Jane Planner', role: 'PLANNER' }],
      recorded_at: '2026-09-08T02:00:00Z',
      justification: 'Looks good',
    });
    expect(decision.plan_id).toBe('PLAN-001');
    expect(decision.action).toBe('APPROVE');
    expect(decision.authorized_by).toBe('Jane Planner');
  });

  it('validates async job status values', () => {
    const job = mapAsyncJob({ jobId: 'JOB-1', status: 'COMPLETED', requestedAt: '2026-09-08T02:00:00Z', resultEndpoint: '/api/v1/plans/PLAN-1' });
    expect(job.status).toBe('COMPLETED');
    expect(job.resultEndpoint).toBe('/api/v1/plans/PLAN-1');
    const unknownStatus = mapAsyncJob({ jobId: 'JOB-2', status: 'SOMETHING_ELSE', requestedAt: '2026-09-08T02:00:00Z' });
    expect(unknownStatus.status).toBe('QUEUED');
  });
});
