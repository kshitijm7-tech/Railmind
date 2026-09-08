'use client';

import React from 'react';
import { useOperationalContext } from '../../context/OperationalContext';
import { StateBadge } from '../state/StateBadge';

export function GlobalContextBar() {
  const { metadata } = useOperationalContext();

  return (
    <div className="global-context-bar" aria-label="Operational context telemetry">
      <div className="context-pill">
        <span>DIVISION:</span>
        <strong>{metadata.divisionName}</strong>
      </div>
      <span style={{ color: 'var(--surface-border-strong)' }}>|</span>
      
      <div className="context-pill">
        <span>CORRIDOR:</span>
        <strong>{metadata.corridorName}</strong>
      </div>
      <span style={{ color: 'var(--surface-border-strong)' }}>|</span>

      <div className="context-pill">
        <span>HORIZON:</span>
        <strong>{metadata.planningHorizonHours}h Horizon</strong>
      </div>
      <span style={{ color: 'var(--surface-border-strong)' }}>|</span>

      <div className="context-pill">
        <span>STATE VERSION:</span>
        <strong style={{ color: 'var(--text-accent)' }}>{metadata.version}</strong>
      </div>
      <span style={{ color: 'var(--surface-border-strong)' }}>|</span>

      <div className="context-pill" style={{ marginLeft: 'auto' }}>
        <span>MODE:</span>
        <StateBadge
          stateType={metadata.mode === 'LIVE' ? 'ACTUAL' : 'SCENARIO'}
          label={metadata.mode === 'LIVE' ? 'LIVE OPERATIONS' : 'WHAT-IF BRANCH'}
        />
      </div>
    </div>
  );
}
