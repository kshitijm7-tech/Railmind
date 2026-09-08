'use client';

import React from 'react';
import { AppShell } from '../../components/layout/AppShell';

export default function SettingsPage() {
  return (
    <AppShell title="System Configuration & Objective Weights" eyebrow="Optimization Parameters">
      <div style={{ maxWidth: '40rem', background: 'var(--surface-panel)', border: '1px solid var(--surface-border)', borderRadius: 'var(--radius-md)', padding: '1.5rem' }}>
        <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.05rem' }}>CP-SAT Objective Weights Configuration</h3>
        <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
          Tune solver parameters for multi-objective optimization (Train Delay vs Maintenance Backlog vs Overrun Risk).
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.25rem' }}>
              <span>Train Delay Penalty (α)</span>
              <strong>5.0</strong>
            </label>
            <input type="range" min="1" max="10" defaultValue="5" style={{ width: '100%' }} />
          </div>

          <div>
            <label style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.25rem' }}>
              <span>Unscheduled Maintenance Penalty (β)</span>
              <strong>4.0</strong>
            </label>
            <input type="range" min="1" max="10" defaultValue="4" style={{ width: '100%' }} />
          </div>

          <div>
            <label style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.25rem' }}>
              <span>Overrun Robustness Penalty (δ)</span>
              <strong>2.0</strong>
            </label>
            <input type="range" min="1" max="10" defaultValue="2" style={{ width: '100%' }} />
          </div>

          <div>
            <label style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.25rem' }}>
              <span>Multi-Dept Possession Bundling Bonus (ε)</span>
              <strong>1.0</strong>
            </label>
            <input type="range" min="1" max="10" defaultValue="1" style={{ width: '100%' }} />
          </div>
        </div>
      </div>
    </AppShell>
  );
}
