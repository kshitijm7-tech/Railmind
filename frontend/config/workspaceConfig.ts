export interface WorkspaceMetadata {
  title: string;
  eyebrow: string;
}

export const WORKSPACE_CONFIG: Record<string, WorkspaceMetadata> = {
  '/': { title: 'Operational Command Center', eyebrow: 'Corridor C-07 | 72h Operational Horizon' },
  '/operations': { title: 'Live Operations', eyebrow: 'Corridor C-07 | Real-Time Telemetry' },
  '/trains': { title: 'Trains & Paths', eyebrow: 'Schedule & Routing Context' },
  '/disruptions': { title: 'Disruptions & Recovery', eyebrow: 'Active Incidents & Alerts' },
  '/maintenance': { title: 'Maintenance Operations', eyebrow: 'Possession & Defect Backlog' },
  '/planning': { title: 'Block Planning', eyebrow: 'Possession Optimization' },
  '/simulation': { title: 'Simulation & What-If', eyebrow: 'Scenario Analysis Engine' },
  '/decisions': { title: 'Decisions & Approvals', eyebrow: 'Authority & Execution Queue' },
  '/audit': { title: 'Audit & Safety Logs', eyebrow: 'System Compliance & Traceability' },
  '/settings': { title: 'System Settings', eyebrow: 'Configuration & Preferences' },
};
