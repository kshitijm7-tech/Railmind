'use client';

import React, { useEffect, useState } from 'react';
import { AppShell } from '../../components/layout/AppShell';
import { CriticalityBadge } from '../../components/railway/RailwayBadges';
import { StateBadge } from '../../components/state/StateBadge';
import { Button } from '../../components/ui/Button';
import { services } from '../../services';
import { Incident } from '../../domain';

export default function DisruptionsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);

  useEffect(() => {
    services.disruption.getActiveIncidents().then(setIncidents);
  }, []);

  return (
    <AppShell
      title="Disruption Management & Incident Recovery"
      eyebrow="Live Incident Telemetry"
      actions={<StateBadge stateType="ACTUAL" label="DISRUPTION INTERCEPTOR ACTIVE" />}
    >
      <div style={{ marginBottom: '1.5rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
        Continuous monitoring of plan deviations, duration overruns, and unexpected track failures.
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {incidents.map(inc => (
          <div
            key={inc.incident_id}
            style={{
              background: 'var(--surface-panel)',
              border: '1px solid var(--status-critical)',
              borderRadius: 'var(--radius-md)',
              padding: '1.25rem'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
                  <span style={{ color: 'var(--status-critical)', fontWeight: 700, fontSize: '0.8rem' }}>
                    🚨 {inc.incident_type}
                  </span>
                  <CriticalityBadge criticality={inc.severity} />
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                    Detected at {new Date(inc.detected_at).toLocaleTimeString()}
                  </span>
                </div>
                <h3 style={{ margin: '0.25rem 0', fontSize: '1.1rem' }}>{inc.title}</h3>
                <p style={{ margin: '0.25rem 0 0 0', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                  {inc.description}
                </p>
              </div>
              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--status-critical)', fontWeight: 600 }}>
                  STATUS: {inc.status.toUpperCase()}
                </span>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                  Est. Clear: {inc.estimated_resolution_time}
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '0.75rem', borderTop: '1px solid var(--surface-border)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Affected Trains:</span>
                {inc.affected_train_ids.map(tid => (
                  <span key={tid} style={{ background: 'var(--surface-elevated)', padding: '0.15rem 0.45rem', borderRadius: 'var(--radius-xs)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>
                    🚆 {tid}
                  </span>
                ))}
              </div>

              <Button variant="danger" size="sm" onClick={() => alert('Triggering CP-SAT Recovery Re-plan (Phase 6)')}>
                ⚡ Generate Recovery Re-Plan
              </Button>
            </div>
          </div>
        ))}
      </div>
    </AppShell>
  );
}
