'use client';

import React, { useEffect, useState, useMemo } from 'react';
import { AppShell } from '../../components/layout/AppShell';
import { CriticalityBadge, SectionBadge } from '../../components/railway/RailwayBadges';
import { StateBadge } from '../../components/state/StateBadge';
import { Button } from '../../components/ui/Button';
import { MetricCard } from '../../components/operational/MetricCard';
import { services } from '../../services';
import { Incident } from '../../domain';
import { AlertTriangle, ShieldAlert, Cpu, ArrowRight, CheckCircle2, RotateCcw, Zap } from 'lucide-react';

export default function DisruptionsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [replanTriggered, setReplanTriggered] = useState<string | null>(null);
  const [replanSuccess, setReplanSuccess] = useState<string | null>(null);

  useEffect(() => {
    services.disruption.getActiveIncidents().then(setIncidents);
  }, []);

  const stats = useMemo(() => {
    const total = incidents.length;
    const criticalCount = incidents.filter((i) => i.severity === 'CRITICAL').length;
    const affectedTrainsCount = new Set(incidents.flatMap((i) => i.affected_train_ids)).size;
    return { total, criticalCount, affectedTrainsCount };
  }, [incidents]);

  const handleGenerateRecovery = async (incidentId: string) => {
    setReplanTriggered(incidentId);
    setReplanSuccess(null);
    try {
      // Simulate/trigger recovery replanning
      setTimeout(() => {
        setReplanTriggered(null);
        setReplanSuccess(`Recovery Re-Plan REC-${incidentId.slice(-4)} generated via E09 CP-SAT. Transferred to Decision Workspace for governed sign-off.`);
      }, 1200);
    } catch {
      setReplanTriggered(null);
    }
  };

  return (
    <AppShell
      title="Disruption Management & Incident Recovery"
      eyebrow="Continuous Incident Telemetry & Dynamic Re-Planning Engine"
      actions={
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <StateBadge stateType="ACTUAL" label="DISRUPTION INTERCEPTOR ACTIVE" />
          <Button
            variant="danger"
            size="sm"
            onClick={() => {
              if (incidents.length > 0) handleGenerateRecovery(incidents[0].incident_id);
            }}
            disabled={incidents.length === 0 || !!replanTriggered}
          >
            {replanTriggered ? 'Computing Re-Plan...' : '⚡ Re-Plan All Incidents'}
          </Button>
        </div>
      }
    >
      <div style={{ marginBottom: '1.25rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
        Continuous monitoring of plan deviations, unexpected track failures, and duration overruns with automated CP-SAT recovery proposals.
      </div>

      {/* KPI Metrics Strip */}
      <div className="cc-kpi-row" style={{ marginBottom: '1.25rem' }}>
        <MetricCard label="Active Incidents" value={stats.total} statusTone={stats.total > 0 ? 'critical' : 'normal'} />
        <MetricCard label="Critical Severity" value={stats.criticalCount} statusTone={stats.criticalCount > 0 ? 'critical' : 'normal'} />
        <MetricCard label="Affected Trains" value={stats.affectedTrainsCount} statusTone={stats.affectedTrainsCount > 0 ? 'warning' : 'normal'} />
        <MetricCard label="Re-Plan Recovery Engine" value="E09 CP-SAT" statusTone="attention" />
      </div>

      {/* AI Proposal Notice Banner */}
      <div className="ai-proposal-banner">
        <div className="ai-proposal-content">
          <ShieldAlert size={24} style={{ color: 'var(--status-critical)', flexShrink: 0 }} />
          <div>
            <div className="ai-proposal-title">
              AI RE-PLAN PROPOSAL — HUMAN CONTROLLER APPROVAL REQUIRED
            </div>
            <div className="ai-proposal-subtitle">
              Automated disruption interceptor has analyzed active track occupancy conflicts. Dynamic re-routing and block rescheduling options are generated as proposals and will never commit to the physical interlocking without human authorization.
            </div>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', flexShrink: 0 }}>
          <Button
            variant="outline"
            size="sm"
            onClick={() => { window.location.href = '/decisions'; }}
          >
            Review in Decision Workspace →
          </Button>
        </div>
      </div>

      {replanSuccess && (
        <div style={{
          padding: '0.75rem 1rem',
          background: 'rgba(16, 185, 129, 0.12)',
          border: '1px solid rgba(16, 185, 129, 0.4)',
          borderRadius: 'var(--radius-sm)',
          color: 'var(--status-normal)',
          fontSize: '0.82rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          marginBottom: '1.25rem',
        }}>
          <CheckCircle2 size={16} />
          <span>{replanSuccess}</span>
        </div>
      )}

      {/* Incidents List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {incidents.length === 0 ? (
          <div style={{
            padding: '2.5rem',
            textAlign: 'center',
            background: 'var(--surface-panel)',
            border: '1px solid var(--surface-border)',
            borderRadius: 'var(--radius-md)',
            color: 'var(--status-normal)'
          }}>
            <CheckCircle2 size={32} style={{ margin: '0 auto 0.75rem' }} />
            <h3 style={{ margin: '0 0 0.25rem', fontSize: '1rem' }}>All Corridor Sections Clear</h3>
            <p style={{ margin: 0, fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              No active disruptions, duration overruns, or signal anomalies reported on Corridor C-07.
            </p>
          </div>
        ) : (
          incidents.map((inc) => {
            const isCritical = inc.severity === 'CRITICAL';
            return (
              <div
                key={inc.incident_id}
                className={`incident-card ${isCritical ? 'incident-card-critical' : ''}`}
              >
                {/* Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.35rem' }}>
                      <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                        color: isCritical ? 'var(--status-critical)' : 'var(--status-warning)',
                        fontWeight: 700,
                        fontSize: '0.8rem',
                        fontFamily: 'var(--font-mono)'
                      }}>
                        <span className={isCritical ? 'radar-crit-dot' : 'radar-live-dot'} />
                        {inc.incident_type}
                      </span>
                      <CriticalityBadge criticality={inc.severity} />
                      <SectionBadge sectionId={inc.section_id} />
                      <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                        ID: {inc.incident_id}
                      </span>
                    </div>
                    <h3 style={{ margin: '0.25rem 0', fontSize: '1.05rem', color: 'var(--text-primary)' }}>
                      {inc.title}
                    </h3>
                    <p style={{ margin: '0.25rem 0 0 0', color: 'var(--text-secondary)', fontSize: '0.82rem', lineHeight: 1.4 }}>
                      {inc.description}
                    </p>
                  </div>
                  <div style={{ textAlign: 'right', display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '2px' }}>
                    <span
                      className="delay-pill"
                      style={{
                        background: isCritical ? 'rgba(239, 68, 68, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                        color: isCritical ? 'var(--status-critical)' : 'var(--status-warning)',
                        border: `1px solid ${isCritical ? 'rgba(239, 68, 68, 0.4)' : 'rgba(245, 158, 11, 0.4)'}`,
                      }}
                    >
                      STATUS: {inc.status.toUpperCase()}
                    </span>
                    <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginTop: '4px' }}>
                      Est. Clear: {inc.estimated_resolution_time}
                    </span>
                  </div>
                </div>

                {/* Proposed Recovery Action Strip */}
                <div style={{
                  background: 'var(--surface-elevated)',
                  border: '1px solid var(--surface-border)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '0.75rem 1rem',
                  marginBottom: '0.75rem',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem', flexWrap: 'wrap', gap: '0.4rem' }}>
                    <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-accent)', textTransform: 'uppercase', letterSpacing: '0.06em', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Cpu size={14} /> Recommended AI Recovery Strategy
                    </span>
                    <span style={{ fontSize: '0.7rem', color: 'var(--status-normal)', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                      Estimated Delay Savings: ~38 min
                    </span>
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                    <span style={{ fontSize: '0.72rem', padding: '2px 6px', background: 'var(--surface-panel)', border: '1px solid var(--surface-border)', borderRadius: '3px', color: 'var(--text-secondary)' }}>
                      1. Reschedule possession window on {inc.section_id} by +60 min
                    </span>
                    <span style={{ fontSize: '0.72rem', padding: '2px 6px', background: 'var(--surface-panel)', border: '1px solid var(--surface-border)', borderRadius: '3px', color: 'var(--text-secondary)' }}>
                      2. Reroute affected express services via bi-directional siding
                    </span>
                    <span style={{ fontSize: '0.72rem', padding: '2px 6px', background: 'var(--surface-panel)', border: '1px solid var(--surface-border)', borderRadius: '3px', color: 'var(--text-secondary)' }}>
                      3. Enforce 30 km/h caution speed order
                    </span>
                  </div>
                </div>

                {/* Affected Trains & Recovery Actions */}
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  paddingTop: '0.75rem',
                  borderTop: '1px solid var(--surface-border)',
                  flexWrap: 'wrap',
                  gap: '0.75rem',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Affected Trains:</span>
                    {inc.affected_train_ids.map((tid) => (
                      <span
                        key={tid}
                        style={{
                          background: 'var(--surface-elevated)',
                          border: '1px solid var(--surface-border)',
                          padding: '0.15rem 0.5rem',
                          borderRadius: 'var(--radius-xs)',
                          fontSize: '0.72rem',
                          fontFamily: 'var(--font-mono)',
                          color: 'var(--text-primary)',
                        }}
                      >
                        🚆 {tid}
                      </span>
                    ))}
                  </div>

                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => {
                        window.location.href = `/simulation?scenarioId=SCN-OVERRUN-01`;
                      }}
                    >
                      Simulate Impact Flow →
                    </Button>
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleGenerateRecovery(inc.incident_id)}
                      disabled={replanTriggered === inc.incident_id}
                    >
                      {replanTriggered === inc.incident_id ? 'Solving CP-SAT...' : '⚡ Generate Recovery Re-Plan'}
                    </Button>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </AppShell>
  );
}

