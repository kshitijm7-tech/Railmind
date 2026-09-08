'use client';

import React, { useEffect, useState } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { MetricCard } from '../components/operational/MetricCard';
import { DecisionCard } from '../components/decision/DecisionCard';
import { DataTable, ColumnDef } from '../components/operational/DataTable';
import { StateBadge } from '../components/state/StateBadge';
import { DepartmentBadge, CriticalityBadge, TrainBadge, SectionBadge } from '../components/railway/RailwayBadges';
import { LoadingState } from '../components/feedback/FeedbackStates';
import { services } from '../services';
import { MaintenanceTask, TrainService, Incident, Recommendation } from '../domain';

export default function CommandCenterPage() {
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [tasks, setTasks] = useState<MaintenanceTask[]>([]);
  const [trains, setTrains] = useState<TrainService[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [rec, tList, trList, incList] = await Promise.all([
          services.recommendations.getLatestRecommendation(),
          services.maintenance.getTasks(),
          services.trains.getTrains(),
          services.disruption.getActiveIncidents()
        ]);
        setRecommendation(rec);
        setTasks(tList.slice(0, 4));
        setTrains(trList.slice(0, 3));
        setIncidents(incList);
      } catch (e) {
        console.error('Failed to load command center data:', e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleApprove = async (id: string) => {
    await services.decisions.submitDecision({
      recommendation_id: id,
      plan_id: recommendation?.plan_id || '',
      state_version: recommendation?.state_version || 'v1024',
      action: 'APPROVE',
      authorized_by: 'Chief Operations Controller (Demo)',
      user_role: 'Operations Controller',
      notes: 'Approved joint night possession for SEC-04 defect correction.'
    });
    alert('Plan Alpha has been authorized and queued for execution!');
  };

  if (loading) {
    return (
      <AppShell>
        <LoadingState message="Loading corridor state & optimization queue..." />
      </AppShell>
    );
  }

  const taskColumns: ColumnDef<MaintenanceTask>[] = [
    { header: 'Task ID', cell: (t) => <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{t.task_id}</span> },
    { header: 'Description', accessorKey: 'title' },
    { header: 'Section', cell: (t) => <SectionBadge sectionId={t.section_id} /> },
    { header: 'Dept', cell: (t) => <DepartmentBadge department={t.department} /> },
    { header: 'Criticality', cell: (t) => <CriticalityBadge criticality={t.criticality} /> },
    { header: 'Priority', cell: (t) => <strong style={{ color: t.priority_score > 90 ? '#ef4444' : '#f59e0b', fontFamily: 'var(--font-mono)' }}>{t.priority_score.toFixed(1)}</strong> }
  ];

  return (
    <AppShell
      actions={
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <StateBadge stateType="ACTUAL" label="TELEMETRY ACTIVE" />
        </div>
      }
    >
      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
        <MetricCard label="Active Maintenance Deficits" value={tasks.length} detail="3 Overdue · 1 Critical Defect" statusTone="warning" />
        <MetricCard label="Corridor Train Paths (72h)" value={48} detail="34 Passenger · 14 Freight" statusTone="attention" />
        <MetricCard label="Scheduled Possessions" value="1 Block (3h)" detail="3 Depts Bundled · SEC-04" statusTone="normal" />
        <MetricCard label="Disruption Incidents" value={incidents.length} detail="1 Overrun Alert Assessing" statusTone="critical" />
      </section>

      {/* Decision Intelligence Recommendation */}
      <section style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
          <div>
            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              ATTENTION & DECISION QUEUE
            </span>
            <h2 style={{ margin: 0, fontSize: '1.15rem' }}>Priority Operational Recommendation</h2>
          </div>
          <StateBadge stateType="PREDICTION" label="CP-SAT SOLVED" />
        </div>

        {recommendation ? (
          <DecisionCard
            recommendation={recommendation}
            onApprove={handleApprove}
            onModify={() => alert('Modify parameters modal would open here in Phase 5')}
            onReject={() => alert('Recommendation rejected')}
          />
        ) : (
          <div style={{ padding: '1rem', background: 'var(--surface-panel)', border: '1px solid var(--surface-border)' }}>
            No pending recommendations.
          </div>
        )}
      </section>

      {/* Corridor Backlog & Active Trains */}
      <section style={{ display: 'grid', gridTemplateColumns: '3fr 2fr', gap: '1.5rem' }}>
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <h3 style={{ margin: 0, fontSize: '1rem' }}>Top Priority Maintenance Backlog</h3>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Explainable AI Scored</span>
          </div>
          <DataTable
            columns={taskColumns}
            data={tasks}
            keyExtractor={(t) => t.task_id}
          />
        </div>

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <h3 style={{ margin: 0, fontSize: '1rem' }}>Active High-Priority Trains</h3>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Schedule Adherence</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {trains.map(tr => (
              <div
                key={tr.train_id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0.75rem 1rem',
                  background: 'var(--surface-panel)',
                  border: '1px solid var(--surface-border)',
                  borderRadius: 'var(--radius-sm)'
                }}
              >
                <div>
                  <TrainBadge trainNumber={tr.train_number} trainType={tr.train_type} priority={tr.priority} />
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                    {tr.name} ({tr.origin_station_id} → {tr.destination_station_id})
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span style={{ color: tr.current_status === 'ON_TIME' ? '#34d399' : '#f59e0b', fontSize: '0.75rem', fontWeight: 600 }}>
                    {tr.current_status}
                  </span>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                    Delay: {tr.current_delay_min}m
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </AppShell>
  );
}
