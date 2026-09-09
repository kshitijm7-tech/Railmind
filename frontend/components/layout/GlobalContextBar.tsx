'use client';

import React from 'react';
import { useOperationalContext } from '../../context/OperationalContext';
import { StateBadge } from '../state/StateBadge';

export function GlobalContextBar() {
  const { metadata } = useOperationalContext();

  return (
    <div className="global-context-bar" aria-label="Operational context telemetry">
      <div className="context-pill">
        <span style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.06em' }}>DIV:</span>
        <strong style={{ color: 'var(--text-primary)' }}>{metadata.divisionName}</strong>
      </div>
      <span style={{ color: 'var(--surface-border-strong)', opacity: 0.6 }}>|</span>
      
      <div className="context-pill">
        <span style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.06em' }}>CORRIDOR:</span>
        <strong style={{ color: 'var(--text-accent)' }}>{metadata.corridorName}</strong>
      </div>
      <span style={{ color: 'var(--surface-border-strong)', opacity: 0.6 }}>|</span>

      <div className="context-pill">
        <span style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.06em' }}>HORIZON:</span>
        <strong style={{ color: 'var(--text-secondary)' }}>{metadata.planningHorizonHours}h Active Window</strong>
      </div>
      <span style={{ color: 'var(--surface-border-strong)', opacity: 0.6 }}>|</span>

      <div className="context-pill">
        <span style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.06em' }}>STATE:</span>
        <strong style={{ color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>{metadata.version}</strong>
      </div>

      <div className="context-pill" style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <span style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.06em' }}>SYSTEM MODE:</span>
        <StateBadge
          stateType={metadata.mode === 'LIVE' ? 'ACTUAL' : 'SCENARIO'}
          label={metadata.mode === 'LIVE' ? 'LIVE OPERATIONS' : 'WHAT-IF BRANCH'}
        />
        {metadata.mode === 'SCENARIO' && metadata.activeScenarioName && (
          <span style={{
            fontWeight: 700,
            color: 'var(--status-attention)',
            fontSize: '0.72rem',
            fontFamily: 'var(--font-mono)',
            padding: '2px 6px',
            background: 'var(--surface-panel)',
            border: '1px solid var(--surface-border)',
            borderRadius: '3px'
          }}>
            [{metadata.activeScenarioName}]
          </span>
        )}
      </div>
    </div>
  );
}
