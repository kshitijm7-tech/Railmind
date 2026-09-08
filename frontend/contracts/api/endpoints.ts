const API_BASE = '/api/v1';

export const API_ENDPOINTS = {
  // System
  HEALTH:               { method: 'GET',   path: '/health' },
  API_VERSION:          { method: 'GET',   path: `${API_BASE}/version` },

  // Infrastructure
  ASSETS_LIST:          { method: 'GET',   path: `${API_BASE}/assets` },
  ASSET_DETAIL:         { method: 'GET',   path: `${API_BASE}/assets/:assetId` },
  TRACK_SECTIONS_LIST:  { method: 'GET',   path: `${API_BASE}/track-sections` },
  TRACK_SECTION_DETAIL: { method: 'GET',   path: `${API_BASE}/track-sections/:sectionId` },
  CORRIDORS_LIST:       { method: 'GET',   path: `${API_BASE}/corridors` },
  CORRIDOR_DETAIL:      { method: 'GET',   path: `${API_BASE}/corridors/:corridorId` },

  // Maintenance
  TASKS_LIST:           { method: 'GET',   path: `${API_BASE}/maintenance/tasks` },
  TASK_DETAIL:          { method: 'GET',   path: `${API_BASE}/maintenance/tasks/:taskId` },
  TASK_CREATE:          { method: 'POST',  path: `${API_BASE}/maintenance/tasks` },
  TASK_UPDATE:          { method: 'PATCH', path: `${API_BASE}/maintenance/tasks/:taskId` },
  DEFECTS_LIST:         { method: 'GET',   path: `${API_BASE}/maintenance/defects` },
  DEFECT_DETAIL:        { method: 'GET',   path: `${API_BASE}/maintenance/defects/:defectId` },
  DEFECT_CREATE:        { method: 'POST',  path: `${API_BASE}/maintenance/defects` },

  // Operations
  TRAINS_LIST:          { method: 'GET',   path: `${API_BASE}/trains` },
  TRAIN_DETAIL:         { method: 'GET',   path: `${API_BASE}/trains/:trainId` },
  TRAIN_PATHS_LIST:     { method: 'GET',   path: `${API_BASE}/train-paths` },
  OPERATIONAL_WINDOWS:  { method: 'GET',   path: `${API_BASE}/operational-windows` },
  TRAIN_IMPACTS_LIST:   { method: 'GET',   path: `${API_BASE}/train-impacts` },

  // Planning — Blocks
  BLOCKS_LIST:          { method: 'GET',   path: `${API_BASE}/blocks` },
  BLOCK_DETAIL:         { method: 'GET',   path: `${API_BASE}/blocks/:blockId` },
  BLOCK_REQUEST:        { method: 'POST',  path: `${API_BASE}/blocks/requests` },
  CANDIDATE_WINDOWS:    { method: 'GET',   path: `${API_BASE}/planning/candidates` },

  // Planning — Plans
  PLANS_LIST:           { method: 'GET',   path: `${API_BASE}/plans` },
  PLAN_DETAIL:          { method: 'GET',   path: `${API_BASE}/plans/:planId` },
  PLAN_VERSIONS:        { method: 'GET',   path: `${API_BASE}/plans/:planId/versions` },
  PLAN_IMPACTS:         { method: 'GET',   path: `${API_BASE}/plans/:planId/impacts` },
  PLAN_METRICS:         { method: 'GET',   path: `${API_BASE}/plans/:planId/metrics` },
  PLAN_GENERATE:        { method: 'POST',  path: `${API_BASE}/planning/generate` }, // -> 202 + AsyncJob
  PLANS_COMPARE:        { method: 'POST',  path: `${API_BASE}/plans/compare` },

  // Simulation
  SIMULATIONS_LIST:     { method: 'GET',   path: `${API_BASE}/simulations` },
  SIMULATION_DETAIL:    { method: 'GET',   path: `${API_BASE}/simulations/:simulationId` },
  SIMULATION_RESULT:    { method: 'GET',   path: `${API_BASE}/simulations/:simulationId/result` },
  SIMULATION_RUN:       { method: 'POST',  path: `${API_BASE}/simulations` }, // -> 202 + AsyncJob

  // Disruptions
  DISRUPTIONS_LIST:     { method: 'GET',   path: `${API_BASE}/disruptions` },
  DISRUPTION_DETAIL:    { method: 'GET',   path: `${API_BASE}/disruptions/:disruptionId` },
  DISRUPTION_CREATE:    { method: 'POST',  path: `${API_BASE}/disruptions` },
  DISRUPTION_UPDATE:    { method: 'PATCH', path: `${API_BASE}/disruptions/:disruptionId` },
  IMPACT_ANALYSIS:      { method: 'POST',  path: `${API_BASE}/disruptions/:disruptionId/impact` },

  // Recovery
  RECOVERY_ANALYZE:     { method: 'POST',  path: `${API_BASE}/recovery/analyze` },
  RECOVERY_CANDIDATES:  { method: 'POST',  path: `${API_BASE}/recovery/candidates` },
  RECOVERY_REPLAN:      { method: 'POST',  path: `${API_BASE}/recovery/replan` }, // -> 202 + AsyncJob
  RECOVERY_PLAN_DETAIL: { method: 'GET',   path: `${API_BASE}/recovery/plans/:recoveryPlanId` },

  // Decisions
  RECOMMENDATIONS_LIST: { method: 'GET',   path: `${API_BASE}/recommendations` },
  RECOMMENDATION_DETAIL:{ method: 'GET',   path: `${API_BASE}/recommendations/:recommendationId` },
  DECISIONS_LIST:       { method: 'GET',   path: `${API_BASE}/decisions` },
  DECISION_DETAIL:      { method: 'GET',   path: `${API_BASE}/decisions/:decisionId` },
  DECISION_APPROVE:     { method: 'POST',  path: `${API_BASE}/decisions/:decisionId/approve` },
  DECISION_REJECT:      { method: 'POST',  path: `${API_BASE}/decisions/:decisionId/reject` },
  DECISION_DEFER:       { method: 'POST',  path: `${API_BASE}/decisions/:decisionId/defer` },

  // Audit
  AUDIT_EVENTS_LIST:    { method: 'GET',   path: `${API_BASE}/audit/events` },

  // Jobs (async polling)
  JOB_STATUS:           { method: 'GET',   path: `${API_BASE}/jobs/:jobId` },
} as const;

export type EndpointKey = keyof typeof API_ENDPOINTS;
