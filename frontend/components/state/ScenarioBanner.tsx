'use client';

import React from 'react';
import { useOperationalContext } from '../../context/OperationalContext';

export function ScenarioBanner() {
  const { metadata, activeScenario, exitScenario } = useOperationalContext();

  if (metadata.mode !== 'SCENARIO' || !activeScenario) {
    return null;
  }

  return (
    <div className="scenario-banner" role="alert">
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <span style={{ fontSize: '1.1rem' }}>⚠️</span>
        <div>
          <strong>SIMULATION / WHAT-IF MODE ACTIVE: </strong>
          <span>{activeScenario.name}</span>
          <span style={{ opacity: 0.85, marginLeft: '0.5rem', fontSize: '0.78rem' }}>
            (Hypothetical branch on state {activeScenario.base_state_version} · Live operational state is unmutated)
          </span>
        </div>
      </div>
      <button
        onClick={exitScenario}
        style={{
          background: 'rgba(251, 146, 60, 0.25)',
          border: '1px solid #fb923c',
          color: '#ffedd5',
          padding: '0.25rem 0.75rem',
          borderRadius: 'var(--radius-sm)',
          cursor: 'pointer',
          fontWeight: 600,
          fontSize: '0.78rem'
        }}
      >
        Exit What-If Mode
      </button>
    </div>
  );
}
