import { 
  RailwayNetwork, 
  MaintenanceTask, 
  TrainService, 
  CrewPool, 
  CandidateBlockWindow, 
  Plan, 
  Recommendation, 
  Incident, 
  AuditEvent,
  Scenario,
  RailwayStateMetadata
} from '../domain';

export const DEMO_STATE_METADATA: RailwayStateMetadata = {
  version: 'v1024',
  divisionId: 'DIV-01',
  divisionName: 'Central Railway Division',
  corridorId: 'CORR-07',
  corridorName: 'Grand Trunk Northern Corridor (6 Stns, 9 Secs)',
  planningHorizonHours: 72,
  mode: 'LIVE',
  lastUpdated: new Date().toISOString()
};

export const DEMO_NETWORK: RailwayNetwork = {
  zone: 'North Central Railway (NCR)',
  division: 'Central Division',
  corridor: 'Corridor C-07',
  stations: [
    { station_id: 'STN-A', name: 'Anandpur Terminal', code: 'ANPT', platforms: 6, tracks: 8, is_junction: true },
    { station_id: 'STN-B', name: 'Bhopal Junction', code: 'BPLJ', platforms: 8, tracks: 12, is_junction: true },
    { station_id: 'STN-C', name: 'Chhatarpur', code: 'CHTP', platforms: 3, tracks: 4, is_junction: false },
    { station_id: 'STN-D', name: 'Devpuri South', code: 'DVPS', platforms: 4, tracks: 6, is_junction: false },
    { station_id: 'STN-E', name: 'Ekta Nagar', code: 'EKTN', platforms: 4, tracks: 5, is_junction: false },
    { station_id: 'STN-F', name: 'Fatehgarh Central', code: 'FTHC', platforms: 7, tracks: 10, is_junction: true },
  ],
  sections: [
    { section_id: 'SEC-01', name: 'Anandpur – Bhopal Up', from_station_id: 'STN-A', to_station_id: 'STN-B', length_km: 24.5, track_count: 2, max_speed_kmph: 130, department_owners: ['Engineering', 'S&T'], criticality: 'HIGH', status: 'OPERATIONAL' },
    { section_id: 'SEC-02', name: 'Anandpur – Bhopal Down', from_station_id: 'STN-B', to_station_id: 'STN-A', length_km: 24.5, track_count: 2, max_speed_kmph: 130, department_owners: ['Engineering', 'S&T'], criticality: 'HIGH', status: 'OPERATIONAL' },
    { section_id: 'SEC-03', name: 'Bhopal – Chhatarpur Main', from_station_id: 'STN-B', to_station_id: 'STN-C', length_km: 18.2, track_count: 1, max_speed_kmph: 110, department_owners: ['Engineering', 'OHE'], criticality: 'CRITICAL', status: 'OPERATIONAL' },
    { section_id: 'SEC-04', name: 'Chhatarpur – Devpuri Single', from_station_id: 'STN-C', to_station_id: 'STN-D', length_km: 32.0, track_count: 1, max_speed_kmph: 100, department_owners: ['Engineering', 'TRD', 'S&T'], criticality: 'CRITICAL', status: 'OPERATIONAL' },
    { section_id: 'SEC-05', name: 'Devpuri – Ekta Nagar Chord', from_station_id: 'STN-D', to_station_id: 'STN-E', length_km: 15.6, track_count: 2, max_speed_kmph: 120, department_owners: ['Engineering', 'S&T'], criticality: 'MEDIUM', status: 'OPERATIONAL' },
    { section_id: 'SEC-06', name: 'Ekta Nagar – Fatehgarh East', from_station_id: 'STN-E', to_station_id: 'STN-F', length_km: 28.4, track_count: 2, max_speed_kmph: 140, department_owners: ['Engineering', 'OHE', 'TRD'], criticality: 'HIGH', status: 'OPERATIONAL' },
    { section_id: 'SEC-07', name: 'Bhopal Loop & Yard Access', from_station_id: 'STN-B', to_station_id: 'STN-C', length_km: 12.0, track_count: 1, max_speed_kmph: 60, department_owners: ['S&T', 'Engineering'], criticality: 'MEDIUM', status: 'OPERATIONAL' },
    { section_id: 'SEC-08', name: 'Devpuri Bypass Goods Line', from_station_id: 'STN-C', to_station_id: 'STN-E', length_km: 42.0, track_count: 1, max_speed_kmph: 75, department_owners: ['Engineering', 'TRD'], criticality: 'LOW', status: 'OPERATIONAL' },
    { section_id: 'SEC-09', name: 'Fatehgarh Terminal Approach', from_station_id: 'STN-E', to_station_id: 'STN-F', length_km: 9.8, track_count: 3, max_speed_kmph: 90, department_owners: ['Engineering', 'S&T', 'OHE'], criticality: 'HIGH', status: 'OPERATIONAL' },
  ],
  assets: [
    { asset_id: 'AST-TRK-01', asset_type: 'TrackAsset', name: 'Turnout Point 104A', section_id: 'SEC-04', department: 'Engineering', health_score: 54, criticality: 'CRITICAL', last_inspected: '2026-08-20', next_due: '2026-09-05', status: 'DEFECTIVE' },
    { asset_id: 'AST-SIG-02', asset_type: 'SignalAsset', name: 'Automatic Block Signal AB-12', section_id: 'SEC-04', department: 'S&T', health_score: 68, criticality: 'HIGH', last_inspected: '2026-08-15', next_due: '2026-09-10', status: 'DEGRADED' },
    { asset_id: 'AST-OHE-03', asset_type: 'OHEAsset', name: 'Catenary Cantilever Mast 44/12', section_id: 'SEC-03', department: 'TRD', health_score: 72, criticality: 'MEDIUM', last_inspected: '2026-08-28', next_due: '2026-09-15', status: 'HEALTHY' },
    { asset_id: 'AST-BRG-04', asset_type: 'Bridge', name: 'Girder Bridge BR-18 (Betwa River)', section_id: 'SEC-06', department: 'Engineering', health_score: 62, criticality: 'HIGH', last_inspected: '2026-08-01', next_due: '2026-09-01', status: 'DEGRADED' },
  ]
};

export const DEMO_MAINTENANCE_TASKS: MaintenanceTask[] = [
  {
    task_id: 'TSK-101',
    title: 'Deep Screening & Tamping over SEC-04 Switch',
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
    status: 'Pending'
  },
  {
    task_id: 'TSK-102',
    title: 'Track Circuit Renewal & Signal Interlocking Test',
    section_id: 'SEC-04',
    asset_id: 'AST-SIG-02',
    department: 'S&T',
    task_type: 'Preventive',
    expected_duration_min: 120,
    duration_estimates: { expected_min: 120, p10_min: 100, p90_min: 150, overrun_probability: 0.14, confidence: 0.88 },
    crew_size_required: 4,
    crew_qualification: 'S&T',
    criticality: 'HIGH',
    overdue_days: 0,
    dependency_task_ids: [],
    earliest_start: '2026-09-08T02:00:00Z',
    priority_score: 82.0,
    status: 'Pending'
  },
  {
    task_id: 'TSK-103',
    title: 'OHE Isolator Inspection & Dropper Replacement',
    section_id: 'SEC-04',
    department: 'TRD',
    task_type: 'Inspection',
    expected_duration_min: 90,
    duration_estimates: { expected_min: 90, p10_min: 75, p90_min: 110, overrun_probability: 0.08, confidence: 0.94 },
    crew_size_required: 3,
    crew_qualification: 'TRD',
    criticality: 'MEDIUM',
    overdue_days: 0,
    dependency_task_ids: [],
    earliest_start: '2026-09-08T02:00:00Z',
    priority_score: 65.0,
    status: 'Pending'
  },
  {
    task_id: 'TSK-104',
    title: 'Bridge Expansion Joint Bearing Greasing',
    section_id: 'SEC-06',
    asset_id: 'AST-BRG-04',
    department: 'Engineering',
    task_type: 'Corrective',
    expected_duration_min: 150,
    duration_estimates: { expected_min: 150, p10_min: 130, p90_min: 200, overrun_probability: 0.22, confidence: 0.85 },
    crew_size_required: 6,
    crew_qualification: 'Engineering',
    criticality: 'HIGH',
    overdue_days: 7,
    dependency_task_ids: [],
    earliest_start: '2026-09-08T06:00:00Z',
    priority_score: 88.0,
    status: 'Pending'
  }
];

export const DEMO_TRAINS: TrainService[] = [
  {
    train_id: 'TRN-12001',
    train_number: '12001',
    name: 'Shatabdi Express',
    train_type: 'Passenger',
    priority: 1,
    origin_station_id: 'STN-A',
    destination_station_id: 'STN-F',
    route_section_ids: ['SEC-01', 'SEC-03', 'SEC-04', 'SEC-05', 'SEC-06'],
    schedule: [
      { section_id: 'SEC-01', scheduled_entry: '2026-09-08T06:00:00Z', scheduled_exit: '2026-09-08T06:15:00Z', delay_minutes: 0 },
      { section_id: 'SEC-03', scheduled_entry: '2026-09-08T06:20:00Z', scheduled_exit: '2026-09-08T06:35:00Z', delay_minutes: 0 },
      { section_id: 'SEC-04', scheduled_entry: '2026-09-08T06:40:00Z', scheduled_exit: '2026-09-08T07:05:00Z', delay_minutes: 0 },
      { section_id: 'SEC-05', scheduled_entry: '2026-09-08T07:10:00Z', scheduled_exit: '2026-09-08T07:22:00Z', delay_minutes: 0 },
      { section_id: 'SEC-06', scheduled_entry: '2026-09-08T07:25:00Z', scheduled_exit: '2026-09-08T07:42:00Z', delay_minutes: 0 }
    ],
    current_status: 'ON_TIME',
    current_delay_min: 0,
    cascading_delay_estimate_min: 0
  },
  {
    train_id: 'TRN-12952',
    train_number: '12952',
    name: 'Rajdhani Superfast',
    train_type: 'Passenger',
    priority: 1,
    origin_station_id: 'STN-F',
    destination_station_id: 'STN-A',
    route_section_ids: ['SEC-06', 'SEC-05', 'SEC-04', 'SEC-03', 'SEC-02'],
    schedule: [
      { section_id: 'SEC-06', scheduled_entry: '2026-09-08T06:15:00Z', scheduled_exit: '2026-09-08T06:32:00Z', delay_minutes: 0 },
      { section_id: 'SEC-05', scheduled_entry: '2026-09-08T06:35:00Z', scheduled_exit: '2026-09-08T06:47:00Z', delay_minutes: 0 },
      { section_id: 'SEC-04', scheduled_entry: '2026-09-08T06:50:00Z', scheduled_exit: '2026-09-08T07:15:00Z', delay_minutes: 0 },
      { section_id: 'SEC-03', scheduled_entry: '2026-09-08T07:20:00Z', scheduled_exit: '2026-09-08T07:35:00Z', delay_minutes: 0 },
      { section_id: 'SEC-02', scheduled_entry: '2026-09-08T07:40:00Z', scheduled_exit: '2026-09-08T07:55:00Z', delay_minutes: 0 }
    ],
    current_status: 'ON_TIME',
    current_delay_min: 0,
    cascading_delay_estimate_min: 0
  },
  {
    train_id: 'TRN-GOODS-88',
    train_number: 'BOXN-8841',
    name: 'Coal Freight Special',
    train_type: 'Goods',
    priority: 4,
    origin_station_id: 'STN-A',
    destination_station_id: 'STN-F',
    route_section_ids: ['SEC-01', 'SEC-07', 'SEC-08', 'SEC-09'],
    schedule: [
      { section_id: 'SEC-01', scheduled_entry: '2026-09-08T03:00:00Z', scheduled_exit: '2026-09-08T03:30:00Z', delay_minutes: 0 },
      { section_id: 'SEC-07', scheduled_entry: '2026-09-08T03:35:00Z', scheduled_exit: '2026-09-08T04:10:00Z', delay_minutes: 0 },
      { section_id: 'SEC-08', scheduled_entry: '2026-09-08T04:15:00Z', scheduled_exit: '2026-09-08T05:20:00Z', delay_minutes: 0 },
      { section_id: 'SEC-09', scheduled_entry: '2026-09-08T05:25:00Z', scheduled_exit: '2026-09-08T05:50:00Z', delay_minutes: 0 }
    ],
    current_status: 'ON_TIME',
    current_delay_min: 0,
    cascading_delay_estimate_min: 0
  }
];

export const DEMO_CREW_POOLS: CrewPool[] = [
  { pool_id: 'CREW-ENG-NIGHT', department: 'Engineering', shift_name: 'Night', shift_window_start: '2026-09-08T00:00:00Z', shift_window_end: '2026-09-08T08:00:00Z', total_crew: 12, available_crew: 4, assigned_crew: 8 },
  { pool_id: 'CREW-ST-NIGHT', department: 'S&T', shift_name: 'Night', shift_window_start: '2026-09-08T00:00:00Z', shift_window_end: '2026-09-08T08:00:00Z', total_crew: 6, available_crew: 2, assigned_crew: 4 },
  { pool_id: 'CREW-TRD-NIGHT', department: 'TRD', shift_name: 'Night', shift_window_start: '2026-09-08T00:00:00Z', shift_window_end: '2026-09-08T08:00:00Z', total_crew: 6, available_crew: 3, assigned_crew: 3 },
  { pool_id: 'CREW-OHE-NIGHT', department: 'OHE', shift_name: 'Night', shift_window_start: '2026-09-08T00:00:00Z', shift_window_end: '2026-09-08T08:00:00Z', total_crew: 4, available_crew: 4, assigned_crew: 0 },
];

export const DEMO_CANDIDATE_WINDOWS: CandidateBlockWindow[] = [
  { window_id: 'WIN-SEC04-NIGHT', section_id: 'SEC-04', earliest_start: '2026-09-08T02:00:00Z', latest_end: '2026-09-08T05:30:00Z', max_duration_min: 210, conflicting_train_ids: [], recommended_usage: 'NIGHT_POSSESSION' },
  { window_id: 'WIN-SEC06-MORNING', section_id: 'SEC-06', earliest_start: '2026-09-08T08:00:00Z', latest_end: '2026-09-08T11:00:00Z', max_duration_min: 180, conflicting_train_ids: ['TRN-GOODS-88'], recommended_usage: 'DAY_LIGHT_WINDOW' },
];

export const DEMO_PLANS: Plan[] = [
  {
    plan_id: 'PLAN-OPT-01',
    name: 'Plan Alpha · Multi-Dept Possession Bundling (Recommended)',
    version: 1,
    state_version: 'v1024',
    strategy: 'Balanced',
    status: 'Recommended',
    blocks: [
      {
        block_id: 'BLK-04-01',
        section_id: 'SEC-04',
        start_time: '2026-09-08T02:15:00Z',
        end_time: '2026-09-08T05:15:00Z',
        duration_min: 180,
        assigned_task_ids: ['TSK-101', 'TSK-102', 'TSK-103'],
        departments_involved: ['Engineering', 'S&T', 'TRD'],
        is_bundled: true,
        status: 'Approved',
        plan_version: 1,
        affected_train_ids: []
      }
    ],
    metrics: {
      total_delay_minutes: 8,
      passenger_trains_affected: 1,
      goods_trains_affected: 0,
      maintenance_tasks_completed: 3,
      maintenance_tasks_unscheduled: 1,
      blocks_count: 1,
      bundled_blocks_count: 1,
      overall_overrun_risk: 0.12,
      objective_score: 42.5
    },
    created_at: '2026-09-08T01:30:00Z',
    solver_runtime_ms: 1420
  },
  {
    plan_id: 'PLAN-OPT-02',
    name: 'Plan Beta · Operations Priority (Delay Minimization)',
    version: 1,
    state_version: 'v1024',
    strategy: 'Operations Priority',
    status: 'Generated',
    blocks: [
      {
        block_id: 'BLK-04-02',
        section_id: 'SEC-04',
        start_time: '2026-09-08T03:00:00Z',
        end_time: '2026-09-08T05:00:00Z',
        duration_min: 120,
        assigned_task_ids: ['TSK-102', 'TSK-103'],
        departments_involved: ['S&T', 'TRD'],
        is_bundled: true,
        status: 'Requested',
        plan_version: 1,
        affected_train_ids: []
      }
    ],
    metrics: {
      total_delay_minutes: 0,
      passenger_trains_affected: 0,
      goods_trains_affected: 0,
      maintenance_tasks_completed: 2,
      maintenance_tasks_unscheduled: 2,
      blocks_count: 1,
      bundled_blocks_count: 1,
      overall_overrun_risk: 0.08,
      objective_score: 68.0
    },
    created_at: '2026-09-08T01:31:00Z',
    solver_runtime_ms: 980
  }
];

export const DEMO_RECOMMENDATION: Recommendation = {
  recommendation_id: 'REC-2026-0908-01',
  state_version: 'v1024',
  plan_id: 'PLAN-OPT-01',
  plan_name: 'Plan Alpha · Multi-Dept Possession Bundling',
  model_version: 'cp-sat-v1.4 / ml-reg-v2.1',
  headline: 'Authorize Shared Possession Block on SEC-04 (02:15 – 05:15 UTC)',
  action_summary: 'Bundle critical Engineering defect task TSK-101 with S&T and TRD inspections into a single 180 min night possession.',
  primary_rationale: 'Bundling 3 departmental tasks into SEC-04 night window prevents 37 mins of future daytime passenger disruption and resolves a CRITICAL 3-day overdue track defect.',
  expected_outcome: {
    total_delay_min: 8,
    affected_trains_count: 1,
    maintenance_completion_pct: 75.0,
    overrun_risk_pct: 12.0
  },
  objective_breakdown: [
    { name: 'Train Delay Penalty (α=5)', weight: 5, value: 8, weighted_contribution: 40, description: '8 min passenger holding absorption' },
    { name: 'Unscheduled Maintenance (β=4)', weight: 4, value: 1, weighted_contribution: 4, description: '1 deferred low-urgency bridge greasing' },
    { name: 'Block Fragmentation (γ=1)', weight: 1, value: 1, weighted_contribution: 1, description: '1 consolidated block instead of 3 separate requests' },
    { name: 'Multi-Department Bundling Bonus (ε=1)', weight: 1, value: 2, weighted_contribution: -2, description: 'Joint possession credit for Eng + S&T + TRD' }
  ],
  constraint_trace: [
    { constraint_name: 'Single Track Exclusivity', category: 'Safety', status: 'SATISFIED', details: 'No train paths overlap on SEC-04 during 02:15-05:15' },
    { constraint_name: 'Night Shift Crew Pool', category: 'Resource', status: 'TIGHT', details: '8 of 12 Engineering crew members deployed' },
    { constraint_name: 'Task Precedence', category: 'Precedence', status: 'SATISFIED', details: 'No active prerequisite dependencies' }
  ],
  alternatives: [
    { plan_id: 'PLAN-OPT-02', name: 'Plan Beta (Operations Priority)', strategy: 'Zero Delay Target', delay_delta_min: -8, tasks_delta: -1, risk_delta_pct: -4, recommendation_rank: 2 }
  ],
  evidence: [
    { source: 'PRIORITY_SCORE', label: 'Task TSK-101 Priority Score', value: '94.5 / 100 (Critical Defect, 3d overdue)', confidence: 0.95, model_version: 'scoring-v1' },
    { source: 'ML_DURATION', label: 'TSK-101 P90 Duration', value: '240 min (Overrun risk 28% if unbuffered)', confidence: 0.91, model_version: 'xgb-dur-v2.1' },
    { source: 'MONTE_CARLO', label: 'Monte Carlo 200 Draws', value: '12% probability of block overrun > 15 min', confidence: 0.92, model_version: 'mc-sim-v1' }
  ],
  created_at: '2026-09-08T01:35:00Z',
  status: 'PENDING_REVIEW'
};

export const DEMO_INCIDENTS: Incident[] = [
  {
    incident_id: 'INC-2026-088',
    incident_type: 'BLOCK_OVERRUN',
    title: 'Block Overrun Alert: BLK-04-01 extending past 05:15 UTC',
    section_id: 'SEC-04',
    severity: 'HIGH',
    status: 'Assessing',
    detected_at: '2026-09-08T05:10:00Z',
    estimated_resolution_time: '2026-09-08T05:55:00Z (+40 min)',
    affected_plan_id: 'PLAN-OPT-01',
    affected_train_ids: ['TRN-12001', 'TRN-12952'],
    affected_block_ids: ['BLK-04-01'],
    description: 'Track tamping machinery encountered ballast obstruction on turnout 104A. Work requires +40 min buffer.'
  }
];

export const DEMO_SCENARIOS: Scenario[] = [
  {
    scenario_id: 'SCN-WHATIF-01',
    name: 'What-If: +45 Min Overrun on SEC-04 Possession',
    scenario_type: 'DURATION_OVERRUN',
    base_state_version: 'v1024',
    description: 'Simulate downstream delay propagation if turnout repair overruns by 45 minutes into morning peak.',
    parameters: { block_id: 'BLK-04-01', overrun_minutes: 45 },
    created_at: '2026-09-08T01:40:00Z'
  },
  {
    scenario_id: 'SCN-WHATIF-02',
    name: 'What-If: Sudden Track Closure on SEC-03 (Betwa River)',
    scenario_type: 'INFRASTRUCTURE_LOSS',
    base_state_version: 'v1024',
    description: 'Simulate full track closure for 6 hours due to water level sensor trigger on bridge BR-18.',
    parameters: { section_id: 'SEC-03', duration_hours: 6 },
    created_at: '2026-09-08T01:45:00Z'
  }
];

export const DEMO_AUDIT_EVENTS: AuditEvent[] = [
  {
    event_id: 'EVT-9001',
    event_type: 'PLAN_GENERATED',
    entity_id: 'PLAN-OPT-01',
    entity_type: 'Plan',
    user: 'OR-Tools CP-SAT Solver Service',
    timestamp: '2026-09-08T01:30:00Z',
    state_version: 'v1024',
    summary: 'Candidate Plan Alpha generated across 9 sections and 72h horizon.'
  },
  {
    event_id: 'EVT-9002',
    event_type: 'PLAN_SIMULATED',
    entity_id: 'PLAN-OPT-01',
    entity_type: 'Plan',
    user: 'Monte Carlo Simulator (N=200)',
    timestamp: '2026-09-08T01:32:00Z',
    state_version: 'v1024',
    summary: 'Robustness validation completed: overall risk 12.0%.'
  }
];
