'use client';

import React, { useMemo } from 'react';
import Link from 'next/link';
import { AppShell } from '../components/layout/AppShell';
import { StateBadge } from '../components/state/StateBadge';
import { Button } from '../components/ui/Button';
import { DataTable, ColumnDef } from '../components/operational/DataTable';
import {
  CriticalityBadge,
  DepartmentBadge,
  SectionBadge,
  TrainBadge,
} from '../components/railway/RailwayBadges';
import { SectionCard } from '../components/command-center/SectionCard';
import { SystemHealthStrip } from '../components/command-center/SystemHealthStrip';
import { NetworkSchematic } from '../components/command-center/NetworkSchematic';
import { AlertsList, type CommandCenterAlert } from '../components/command-center/AlertsList';
import { MetricCard } from '../components/operational/MetricCard';
import { useCommandCenterData } from '../hooks/useCommandCenterData';
import { deriveCommandCenterAlerts } from '../hooks/deriveCommandCenterAlerts';
import type {
  DecisionRecord,
  Incident,
  MaintenanceTask,
  Plan,
  Recommendation,
  TrainService,
} from '../domain';

export default function CommandCenterPage() {
  const { data, loading, reload, lastRefreshedAt } = useCommandCenterData();

  const backendHealthy = data.system.status === 'success' && data.system.data?.healthy === true;

  const tasks = data.maintenance.data ?? [];
  const defects = data.defects.data ?? [];
  const trains = data.trains.data ?? [];
  const plans = data.plans.data ?? [];
  const decisions = data.decisions.data ?? [];
  const incidents = data.incidents.data ?? [];
  const recommendation = data.recommendation.data ?? null;
  const network = data.network.data;

  const alerts: CommandCenterAlert[] = useMemo(
    () =>
      deriveCommandCenterAlerts({
        tasks,
        defects,
        incidents,
        trains,
        plans,
        decisions,
        recommendation,
        backendHealthy,
      }),
    [tasks, defects, incidents, trains, plans, decisions, recommendation, backendHealthy],
  );

  const maintenanceMetrics = useMemo(() => {
    let critical = 0;
    let high = 0;
    let open = 0;
    let overdue = 0;
    let inProgress = 0;
    for (const task of tasks) {
      if (task.criticality === 'CRITICAL') critical += 1;
      if (task.criticality === 'HIGH') high += 1;
      if (task.status === 'Pending' || task.status === 'Scheduled') open += 1;
      if (task.overdue_days > 0) overdue += 1;
      if (task.status === 'In Progress') inProgress += 1;
    }
    return { critical, high, open, overdue, inProgress, total: tasks.length };
  }, [tasks]);

  const trainMetrics = useMemo(() => {
    let delayed = 0;
    let onTime = 0;
    let totalDelay = 0;
    for (const train of trains) {
      if (train.current_status === 'DELAYED' || train.current_delay_min > 0) {
        delayed += 1;
        totalDelay += train.current_delay_min;
      }
      if (train.current_status === 'ON_TIME') onTime += 1;
    }
    return { total: trains.length, delayed, onTime, totalDelay };
  }, [trains]);

  const planMetrics = useMemo(() => {
    let generated = 0;
    let approved = 0;
    let rejected = 0;
    let recommended = 0;
    let active = 0;
    for (const plan of plans) {
      if (plan.status === 'Generated') generated += 1;
      if (plan.status === 'Approved') approved += 1;
      if (plan.status === 'Rejected') rejected += 1;
      if (plan.status === 'Recommended') recommended += 1;
      if (plan.status === 'Approved' && plan.blocks.length > 0) active += 1;
    }
    return { total: plans.length, generated, approved, rejected, recommended, active };
  }, [plans]);

  const decisionMetrics = useMemo(() => {
    let pending = 0;
    let approved = 0;
    let rejected = 0;
    for (const decision of decisions) {
      if (decision.action === 'APPROVE') approved += 1;
      else if (decision.action === 'REJECT') rejected += 1;
      else pending += 1;
    }
    return { pending, approved, rejected, total: decisions.length };
  }, [decisions]);

  const networkSections = network?.sections ?? [];
  const assetsBySection = useMemo(() => {
    const map: Record<string, number> = {};
    for (const asset of network?.assets ?? []) {
      map[asset.section_id] = (map[asset.section_id] ?? 0) + 1;
    }
    return map;
  }, [network]);

  const networkSummary = useMemo(() => {
    let operational = 0;
    let restricted = 0;
    for (const s of networkSections) {
      if (s.status === 'OPERATIONAL') operational += 1;
      if (s.status === 'RESTRICTED' || s.status === 'BLOCKED' || s.status === 'MAINTENANCE') restricted += 1;
    }
    return { total: networkSections.length, operational, restricted };
  }, [networkSections]);

  const lastRefreshLabel = lastRefreshedAt ? new Date(lastRefreshedAt).toLocaleTimeString() : '\u2014';

  return (
    <AppShell
      title="Operational Command Center"
      eyebrow="Real-Time Corridor Awareness · F02"
      actions={
        <div className="cc-top-actions">
          <StateBadge stateType="ACTUAL" label="TELEMETRY ACTIVE" />
          <Button variant="outline" size="sm" onClick={reload} disabled={loading} aria-label="Refresh command center">
            {'\u27f3 Refresh'}
         </Button>
       </div>
      }
    >
      <SystemHealthStrip snapshot={data.system} />

      <div className="cc-meta-row" aria-label="Refresh metadata">
        <span>
          Last refreshed: <strong>{lastRefreshLabel}</strong>
       </span>
        <span>·</span>
        <span>
          Section load:{' '}
          {Object.values(data).filter((s) => s.status === 'success').length}/{Object.keys(data).length} sections live
       </span>
        {loading && <span className="cc-loading-inline">Refreshing…</span>}
     </div>

      <SectionCard
        eyebrow="PRIORITY 1 · ATTENTION"
        title="Operational Alerts"
        status={data.system.status === 'success' || data.system.status === 'idle' ? 'success' : 'loading'}
        href="/disruptions"
        hrefLabel="Open Disruptions"
        testId="cc-section-alerts"
      >
        <AlertsList alerts={alerts} />
     </SectionCard>

      <SectionCard
        eyebrow="NETWORK STATE"
        title="Corridor Schematic"
        status={data.network.status}
        errorMessage={data.network.errorMessage}
        onRetry={reload}
        href="/operations"
        hrefLabel="Open Operations"
        testId="cc-section-network"
      >
        {network ? (
          <NetworkSchematic
            corridorName={`${network.zone} · ${network.corridor}`}
            sections={networkSections}
            summary={networkSummary}
            assetsBySection={assetsBySection}
          />
        ) : (
          <div className="cc-empty">No corridor topology available</div>
        )}
      </SectionCard>

      <div className="cc-two-col">
        <SectionCard
          eyebrow="MAINTENANCE SITUATION"
          title="Maintenance Backlog"
          status={data.maintenance.status}
          errorMessage={data.maintenance.errorMessage}
          onRetry={reload}
          href="/maintenance"
          hrefLabel="Open Maintenance"
          testId="cc-section-maintenance"
        >
          <div className="cc-kpi-row" aria-label="Maintenance key metrics">
            <MetricCard label="Critical" value={maintenanceMetrics.critical} statusTone="critical" />
            <MetricCard label="High" value={maintenanceMetrics.high} statusTone="warning" />
            <MetricCard label="Open" value={maintenanceMetrics.open} statusTone="attention" />
            <MetricCard label="Overdue" value={maintenanceMetrics.overdue} statusTone="critical" />
         </div>
          <TopMaintenanceTable tasks={tasks} limit={5} />
       </SectionCard>

        <SectionCard
          eyebrow="DEFECTS"
          title="Active Defects & Critical Assets"
          status={data.defects.status}
          errorMessage={data.defects.errorMessage}
          onRetry={reload}
          href="/maintenance"
          hrefLabel="Open Maintenance"
          testId="cc-section-defects"
        >
          <DefectsList defects={defects} />
       </SectionCard>
     </div>

      <div className="cc-two-col">
        <SectionCard
          eyebrow="OPERATIONAL IMPACT"
          title="Train Movement"
          status={data.trains.status}
          errorMessage={data.trains.errorMessage}
          onRetry={reload}
          href="/trains"
          hrefLabel="Open Trains"
          testId="cc-section-trains"
        >
          <div className="cc-kpi-row" aria-label="Train key metrics">
            <MetricCard label="Trains in dataset" value={trainMetrics.total} statusTone="attention" />
            <MetricCard
              label="Delayed"
              value={trainMetrics.delayed}
              statusTone={trainMetrics.delayed > 0 ? 'warning' : 'normal'}
            />
            <MetricCard label="On time" value={trainMetrics.onTime} statusTone="normal" />
            <MetricCard
              label="Reported delay"
              value={`${trainMetrics.totalDelay}m`}
              statusTone={trainMetrics.totalDelay > 60 ? 'warning' : 'normal'}
            />
         </div>
          <TopTrainsList trains={trains} limit={4} />
          <p className="cc-hint">
            Reported delays reflect current telemetry only; computed impact from plans and simulations will be
            surfaced in later phases.
         </p>
       </SectionCard>

        <SectionCard
          eyebrow="PLANNING STATUS"
          title="Plans & Pending Reviews"
          status={data.plans.status}
          errorMessage={data.plans.errorMessage}
          onRetry={reload}
          href="/planning"
          hrefLabel="Open Planning"
          testId="cc-section-planning"
        >
          <div className="cc-kpi-row" aria-label="Planning key metrics">
            <MetricCard label="Total plans" value={planMetrics.total} statusTone="attention" />
            <MetricCard label="Recommended" value={planMetrics.recommended} statusTone="attention" />
            <MetricCard label="Approved" value={planMetrics.approved} statusTone="normal" />
            <MetricCard
              label="Rejected"
              value={planMetrics.rejected}
              statusTone={planMetrics.rejected > 0 ? 'warning' : 'normal'}
            />
         </div>
          <TopPlansList plans={plans} limit={4} />
       </SectionCard>
     </div>

      <SectionCard
        eyebrow="DECISIONS REQUIRING ATTENTION"
        title="Human-in-the-Loop Queue"
        status={data.decisions.status}
        errorMessage={data.decisions.errorMessage}
        onRetry={reload}
        href="/decisions"
        hrefLabel="Open Decisions"
        testId="cc-section-decisions"
      >
        <DecisionQueue
          recommendation={recommendation}
          decisions={decisions}
          recommendationStatus={data.recommendation.status}
        />
     </SectionCard>

      <footer className="cc-footer">
        <span>
          Built from F01 service abstraction. Backend:{' '}
          <code>{process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000'}</code> · Mode:{' '}
          <code>{process.env.NEXT_PUBLIC_API_MODE ?? 'auto'}</code>
       </span>
        <Link href="/audit" className="cc-footer-link">
          Open audit log →
       </Link>
     </footer>
   </AppShell>
  );
}

function TopMaintenanceTable({ tasks, limit }: { tasks: MaintenanceTask[]; limit: number }) {
  const top = useMemo(
    () =>
      [...tasks]
        .sort((a, b) => {
          const aOver = a.overdue_days > 0 ? 1 : 0;
          const bOver = b.overdue_days > 0 ? 1 : 0;
          if (aOver !== bOver) return bOver - aOver;
          return b.priority_score - a.priority_score;
        })
        .slice(0, limit),
    [tasks, limit],
  );

  const columns: ColumnDef<MaintenanceTask>[] = [
    {
      header: 'Task',
      cell: (t) => <strong style={{ fontFamily: 'var(--font-mono)' }}>{t.task_id}</strong>,
    },
    { header: 'Title', accessorKey: 'title' },
    { header: 'Section', cell: (t) => <SectionBadge sectionId={t.section_id} /> },
    { header: 'Dept', cell: (t) => <DepartmentBadge department={t.department} /> },
    { header: 'Criticality', cell: (t) => <CriticalityBadge criticality={t.criticality} /> },
    {
      header: 'Overdue',
      cell: (t) =>
        t.overdue_days > 0 ? (
          <span style={{ color: 'var(--status-critical)', fontWeight: 700 }}>+{t.overdue_days}d</span>
        ) : (
          <span style={{ color: 'var(--text-muted)' }}>On schedule</span>
        ),
    },
    {
      header: 'Priority',
      cell: (t) => (
        <strong
          style={{
            fontFamily: 'var(--font-mono)',
            color: t.priority_score > 80 ? 'var(--status-critical)' : t.priority_score > 60 ? 'var(--status-warning)' : 'var(--text-accent)',
          }}
        >
          {t.priority_score.toFixed(0)}
       </strong>
      ),
    },
  ];

  return (
    <DataTable
      columns={columns}
      data={top}
      keyExtractor={(t) => t.task_id}
      emptyMessage="No maintenance tasks require attention."
    />
  );
}

function DefectsList({ defects }: { defects: Incident[] }) {
  if (defects.length === 0) {
    return (
      <div className="cc-empty" role="status">
        <strong>No active defects</strong>
        <p>No critical or high-severity defects are reported for the current scope</p>
     </div>
    );
  }
  const visible = defects.slice(0, 6);
  return (
    <ul className="cc-defect-list" aria-label="Active defects">
      {visible.map((defect) => (
        <li key={defect.incident_id} className="cc-defect-item">
          <div className="cc-defect-meta">
            <SectionBadge sectionId={defect.section_id} />
            <CriticalityBadge criticality={defect.severity} />
         </div>
          <div className="cc-defect-body">
            <strong>{defect.title}</strong>
            <p>{defect.description}</p>
         </div>
          <span className="cc-defect-time">
            {defect.detected_at ? new Date(defect.detected_at).toLocaleString() : '—'}
         </span>
       </li>
      ))}
   </ul>
  );
}

function TopTrainsList({ trains, limit }: { trains: TrainService[]; limit: number }) {
  const top = trains.slice(0, limit);
  if (top.length === 0) {
    return <div className="cc-empty">No train telemetry available for the corridor dataset</div>;
  }
  return (
    <ul className="cc-train-list" aria-label="Train telemetry">
      {top.map((train) => (
        <li key={train.train_id} className="cc-train-item">
          <TrainBadge trainNumber={train.train_number} trainType={train.train_type} priority={train.priority} />
          <div className="cc-train-body">
            <strong>{train.name}</strong>
            <span>
              {train.origin_station_id} → {train.destination_station_id} · {train.route_section_ids.length} sections
           </span>
         </div>
          <div className="cc-train-status">
            <span className={train.current_status === 'ON_TIME' ? 'cc-train-ok' : 'cc-train-warn'}>
              ● {train.current_status}
           </span>
            <span className="cc-train-delay">{train.current_delay_min}m delay</span>
         </div>
       </li>
      ))}
   </ul>
  );
}

function TopPlansList({ plans, limit }: { plans: Plan[]; limit: number }) {
  const top = plans.slice(0, limit);
  if (top.length === 0) {
    return <div className="cc-empty">No plans generated yet for the current horizon</div>;
  }
  return (
    <ul className="cc-plan-list" aria-label="Plan summary">
      {top.map((plan) => (
        <li key={plan.plan_id} className="cc-plan-item">
          <div className="cc-plan-meta">
            <strong className="cc-plan-id">{plan.plan_id}</strong>
            <span className="cc-plan-strategy">{plan.strategy}</span>
         </div>
          <div className="cc-plan-body">
            <strong>{plan.name}</strong>
            <span>
              {plan.metrics.total_delay_minutes} min predicted delay ·{' '}
              {plan.metrics.maintenance_tasks_completed} task(s) · {plan.blocks.length} block(s)
           </span>
         </div>
          <span
            className={`cc-plan-status cc-plan-status-${plan.status.toLowerCase().replace(/\s+/g, '-')}`}
          >
            {plan.status}
         </span>
       </li>
      ))}
   </ul>
  );
}

interface DecisionQueueProps {
  recommendation: Recommendation | null;
  decisions: DecisionRecord[];
  recommendationStatus: 'idle' | 'loading' | 'success' | 'error';
}

function DecisionQueue({ recommendation, decisions, recommendationStatus }: DecisionQueueProps) {
  const recent = decisions.slice(0, 3);

  return (
    <div className="cc-decision-grid">
      <article className="cc-decision-pending" aria-label="Pending recommendation">
        <span className="cc-section-eyebrow">SYSTEM RECOMMENDATION</span>
        {recommendationStatus === 'loading' && <p className="cc-hint">Loading latest recommendation…</p>}
        {recommendationStatus === 'error' && (
          <p className="cc-decision-empty">
            Could not load the latest recommendation. See Decision Workspace for full history.
         </p>
        )}
        {recommendationStatus === 'success' && recommendation && (
          <>
            <h3 className="cc-decision-title">{recommendation.headline}</h3>
            <p className="cc-decision-detail">{recommendation.action_summary}</p>
            <div className="cc-decision-row">
              <span>
                <strong>Plan</strong> {recommendation.plan_name}
             </span>
              <span>
                <strong>State</strong> {recommendation.state_version}
             </span>
              <span>
                <strong>Risk</strong> {recommendation.expected_outcome.overrun_risk_pct.toFixed(0)}%
             </span>
           </div>
            <p className="cc-hint">
              Recommendation only — human authorization required before operational effect.
           </p>
            <Link href="/decisions" className="cc-decision-link">
              Review & authorize →
           </Link>
          </>
        )}
        {recommendationStatus === 'success' && !recommendation && (
          <p className="cc-decision-empty">
            No pending recommendations. The optimization engine has no plans awaiting human authorization.
         </p>
        )}
     </article>

      <article className="cc-decision-history" aria-label="Recent decisions">
        <span className="cc-section-eyebrow">RECENT HUMAN DECISIONS</span>
        {recent.length === 0 ? (
          <p className="cc-decision-empty">No authorization actions recorded in this session</p>
        ) : (
          <ul className="cc-decision-history-list">
            {recent.map((d) => (
              <li key={d.decision_id} className="cc-decision-history-item">
                <span className={`cc-decision-tag cc-decision-tag-${d.action.toLowerCase()}`}>
                  {d.action}
               </span>
                <div>
                  <strong>Plan {d.plan_id}</strong>
                  <span>
                    {d.authorized_by} ({d.user_role})
                 </span>
               </div>
                <span className="cc-decision-time">{new Date(d.timestamp).toLocaleTimeString()}</span>
             </li>
            ))}
         </ul>
        )}
     </article>
   </div>
  );
}
