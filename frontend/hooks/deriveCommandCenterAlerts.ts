'use client';

import type {
  DecisionRecord,
  Incident,
  MaintenanceTask,
  Plan,
  Recommendation,
  TrainService,
} from '../domain';
import type { CommandCenterAlert } from '../components/command-center/AlertsList';

/**
 * F02 — Derive alerts deterministically from real backend data.
 * No fake operational facts. Alerts disappear when their cause resolves.
 */
export function deriveCommandCenterAlerts(input: {
  tasks: MaintenanceTask[];
  defects: Incident[];
  incidents: Incident[];
  trains: TrainService[];
  plans: Plan[];
  decisions: DecisionRecord[];
  recommendation: Recommendation | null;
  backendHealthy: boolean;
}): CommandCenterAlert[] {
  const alerts: CommandCenterAlert[] = [];

  if (!input.backendHealthy) {
    alerts.push({
      id: 'system:backend-down',
      severity: 'CRITICAL',
      title: 'RailMind backend unavailable',
      detail: 'Operational data shown is from the local mock fallback. Live updates are paused.',
      source: 'system probe',
      href: '/',
    });
  }

  for (const incident of input.incidents) {
    if (incident.status === 'Resolved') continue;
    const severity = mapIncidentSeverity(incident.severity);
    alerts.push({
      id: `incident:${incident.incident_id}`,
      severity,
      title: `${humanizeIncidentType(incident.incident_type)} · ${incident.section_id}`,
      detail:
        incident.description ||
        `${incident.affected_train_ids.length} train(s) and ${incident.affected_block_ids.length} block(s) impacted.`,
      source: 'disruption telemetry',
      href: '/disruptions',
    });
  }

  for (const defect of input.defects) {
    if (defect.severity !== 'CRITICAL' && defect.severity !== 'HIGH') continue;
    if (defect.status === 'Resolved') continue;
    alerts.push({
      id: `defect:${defect.incident_id}`,
      severity: defect.severity === 'CRITICAL' ? 'CRITICAL' : 'WARNING',
      title: `${humanizeDefectType(defect.incident_type)} defect · ${defect.section_id}`,
      detail: defect.description,
      source: 'defect telemetry',
      href: '/maintenance',
    });
  }

  for (const task of input.tasks) {
    if (task.status === 'Completed' || task.status === 'Cancelled') continue;
    if (task.overdue_days <= 0) continue;
    const severity: 'CRITICAL' | 'WARNING' =
      task.criticality === 'CRITICAL' || task.criticality === 'HIGH' ? 'CRITICAL' : 'WARNING';
    alerts.push({
      id: `task-overdue:${task.task_id}`,
      severity,
      title: `Overdue maintenance · ${task.task_id}`,
      detail: `${task.title} is ${task.overdue_days} day(s) past its planned finish on ${task.section_id}.`,
      source: 'maintenance backlog',
      href: '/maintenance',
    });
  }

  if (input.recommendation && input.recommendation.status === 'PENDING_REVIEW') {
    alerts.push({
      id: `recommendation:${input.recommendation.recommendation_id}`,
      severity: 'WARNING',
      title: 'Recommendation awaiting human authorization',
      detail: `${input.recommendation.headline} — requires APPROVE/REJECT by an authorized role.`,
      source: 'decision intelligence',
      href: '/decisions',
    });
  }

  const approvedPendingExecution = input.decisions.find(
    (d) => d.action === 'APPROVE' && d.notes?.toLowerCase().includes('pending'),
  );
  if (approvedPendingExecution) {
    alerts.push({
      id: `approved-pending:${approvedPendingExecution.decision_id}`,
      severity: 'INFO',
      title: 'Plan approved, awaiting operational execution',
      detail: `Plan ${approvedPendingExecution.plan_id} approved by ${approvedPendingExecution.authorized_by}.`,
      source: 'decision log',
      href: '/decisions',
    });
  }

  const delayedTrains = input.trains.filter((t) => t.current_status === 'DELAYED' && t.current_delay_min > 0);
  if (delayedTrains.length > 0) {
    const total = delayedTrains.reduce((acc, t) => acc + t.current_delay_min, 0);
    alerts.push({
      id: 'trains:delays',
      severity: total > 60 ? 'WARNING' : 'INFO',
      title: `${delayedTrains.length} train(s) reporting delay`,
      detail: `Combined reported delay: ${total} min across the corridor dataset.`,
      source: 'train telemetry',
      href: '/trains',
    });
  }

  const plans = input.plans;
  const blockedPlans = plans.filter((p) => p.status === 'Rejected' || p.status === 'Invalidated');
  if (blockedPlans.length > 0) {
    alerts.push({
      id: 'planning:blocked',
      severity: 'WARNING',
      title: `${blockedPlans.length} plan(s) blocked / rejected`,
      detail: 'See planning workspace for invalidation causes and required re-runs.',
      source: 'planning',
      href: '/planning',
    });
  }

  return alerts;
}

function mapIncidentSeverity(value: unknown): 'CRITICAL' | 'WARNING' | 'INFO' {
  const v = typeof value === 'string' ? value.toUpperCase() : '';
  if (v === 'CRITICAL') return 'CRITICAL';
  if (v === 'HIGH' || v === 'MAJOR') return 'WARNING';
  return 'INFO';
}

function humanizeIncidentType(value: string): string {
  return value
    .toLowerCase()
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
}

function humanizeDefectType(value: string): string {
  return humanizeIncidentType(value);
}
