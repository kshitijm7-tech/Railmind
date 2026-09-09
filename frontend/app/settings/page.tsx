'use client';

import React, { useState } from 'react';
import { AppShell } from '../../components/layout/AppShell';
import { Button } from '../../components/ui/Button';
import { StateBadge } from '../../components/state/StateBadge';
import { Sliders, RotateCcw, Save, CheckCircle2, Cpu, Info } from 'lucide-react';

export default function SettingsPage() {
  const [delayWeight, setDelayWeight] = useState(5.0);
  const [backlogWeight, setBacklogWeight] = useState(4.0);
  const [robustnessWeight, setRobustnessWeight] = useState(2.0);
  const [bundlingWeight, setBundlingWeight] = useState(1.0);
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleReset = () => {
    setDelayWeight(5.0);
    setBacklogWeight(4.0);
    setRobustnessWeight(2.0);
    setBundlingWeight(1.0);
    setSavedSuccess(false);
  };

  const handleSave = () => {
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  return (
    <AppShell
      title="System Configuration & Objective Weights"
      eyebrow="Mathematical Solver Hyperparameters & Constraint Tuning"
      actions={
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <StateBadge stateType="PLAN" label="SOLVER ENGINE: E09 CP-SAT" />
        </div>
      }
    >
      <div style={{ marginBottom: '1.25rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
        Configure multi-objective penalty weights and search parameters for Google OR-Tools CP-SAT joint possession optimization.
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(320px, 44rem) 1fr', gap: '1.5rem', alignItems: 'start' }}>
        {/* Main Weight Sliders Card */}
        <div style={{
          background: 'var(--surface-panel)',
          border: '1px solid var(--surface-border)',
          borderRadius: 'var(--radius-md)',
          padding: '1.5rem',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', borderBottom: '1px solid var(--surface-border)', paddingBottom: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Sliders size={18} style={{ color: 'var(--text-accent)' }} />
              <h3 style={{ margin: 0, fontSize: '1.05rem', color: 'var(--text-primary)' }}>
                Multi-Objective Penalty Function Weights
              </h3>
            </div>
            <span style={{ fontSize: '0.7rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
              FORMULATION: MIN Σ(w_i · Cost_i)
            </span>
          </div>

          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: '1.5rem', lineHeight: 1.4 }}>
            Adjusting weights dynamically re-balances the CP-SAT objective function when candidate plans are generated. Hard constraints (headway, power-off rules, curfew) are always strictly enforced regardless of weight values.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Delay Weight */}
            <div style={{ background: 'var(--surface-elevated)', border: '1px solid var(--surface-border)', borderRadius: 'var(--radius-sm)', padding: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <div>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>Train Delay Penalty (α)</span>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Penalizes aggregate passenger & freight delays (min)</div>
                </div>
                <span style={{ fontSize: '1.1rem', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--text-accent)' }}>
                  {delayWeight.toFixed(1)}x
                </span>
              </div>
              <input
                type="range"
                min="0.5"
                max="10"
                step="0.5"
                value={delayWeight}
                onChange={(e) => setDelayWeight(parseFloat(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--text-accent)', cursor: 'pointer' }}
              />
            </div>

            {/* Backlog Weight */}
            <div style={{ background: 'var(--surface-elevated)', border: '1px solid var(--surface-border)', borderRadius: 'var(--radius-sm)', padding: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <div>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>Unscheduled Maintenance Penalty (β)</span>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Penalizes deferred critical and high priority tasks</div>
                </div>
                <span style={{ fontSize: '1.1rem', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--state-prediction)' }}>
                  {backlogWeight.toFixed(1)}x
                </span>
              </div>
              <input
                type="range"
                min="0.5"
                max="10"
                step="0.5"
                value={backlogWeight}
                onChange={(e) => setBacklogWeight(parseFloat(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--state-prediction)', cursor: 'pointer' }}
              />
            </div>

            {/* Robustness Weight */}
            <div style={{ background: 'var(--surface-elevated)', border: '1px solid var(--surface-border)', borderRadius: 'var(--radius-sm)', padding: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <div>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>Overrun Robustness Penalty (δ)</span>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Penalizes low buffer margins on high-risk possession tasks</div>
                </div>
                <span style={{ fontSize: '1.1rem', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--status-warning)' }}>
                  {robustnessWeight.toFixed(1)}x
                </span>
              </div>
              <input
                type="range"
                min="0.5"
                max="10"
                step="0.5"
                value={robustnessWeight}
                onChange={(e) => setRobustnessWeight(parseFloat(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--status-warning)', cursor: 'pointer' }}
              />
            </div>

            {/* Bundling Bonus */}
            <div style={{ background: 'var(--surface-elevated)', border: '1px solid var(--surface-border)', borderRadius: 'var(--radius-sm)', padding: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <div>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>Cross-Department Bundling Bonus (ε)</span>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Rewards simultaneous Civil + S&T + TRD work inside single block</div>
                </div>
                <span style={{ fontSize: '1.1rem', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--status-normal)' }}>
                  {bundlingWeight.toFixed(1)}x
                </span>
              </div>
              <input
                type="range"
                min="0.5"
                max="5"
                step="0.5"
                value={bundlingWeight}
                onChange={(e) => setBundlingWeight(parseFloat(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--status-normal)', cursor: 'pointer' }}
              />
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid var(--surface-border)' }}>
            <Button variant="secondary" size="sm" onClick={handleReset}>
              <RotateCcw size={14} style={{ marginRight: '4px' }} />
              Reset Defaults
            </Button>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              {savedSuccess && (
                <span style={{ color: 'var(--status-normal)', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 600 }}>
                  <CheckCircle2 size={15} /> Weights Updated
                </span>
              )}
              <Button variant="primary" size="sm" onClick={handleSave}>
                <Save size={14} style={{ marginRight: '4px' }} />
                Save & Apply to E09
              </Button>
            </div>
          </div>
        </div>

        {/* Informational SCADA Side Panel */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{
            background: 'var(--surface-panel)',
            border: '1px solid var(--surface-border)',
            borderRadius: 'var(--radius-md)',
            padding: '1.25rem',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', color: 'var(--text-accent)' }}>
              <Cpu size={18} />
              <h4 style={{ margin: 0, fontSize: '0.9rem' }}>CP-SAT Mathematical Guarantees</h4>
            </div>
            <p style={{ margin: '0 0 0.75rem 0', fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
              The CP-SAT engine guarantees that no weight configuration can override hard safety invariants. Track occupancy overlaps and power distribution lockouts are formulated as strict boolean implications.
            </p>
            <ul style={{ margin: 0, paddingLeft: '1.1rem', fontSize: '0.72rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
              <li>Hard Headway: Minimum 10-minute buffer</li>
              <li>Traction Power: Curfew non-concurrency</li>
              <li>Resource Availability: Crew & machinery bounds</li>
            </ul>
          </div>

          <div style={{
            background: 'var(--surface-panel)',
            border: '1px solid var(--surface-border)',
            borderRadius: 'var(--radius-md)',
            padding: '1.25rem',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', color: 'var(--status-warning)' }}>
              <Info size={18} />
              <h4 style={{ margin: 0, fontSize: '0.9rem' }}>Operational Guidance</h4>
            </div>
            <p style={{ margin: 0, fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
              During festival seasons or peak passenger load, increase <strong>Train Delay Penalty (α)</strong> to 8.0+. During major corridor renewal drives, elevate <strong>Backlog Penalty (β)</strong> to 7.0+ to force possession granting.
            </p>
          </div>
        </div>
      </div>
    </AppShell>
  );
}

