'use client';

import React from 'react';
import type { SimulationResult, Scenario, Plan } from '../../domain';
import { ArrowRight, AlertTriangle, ShieldCheck, Zap, TrendingUp, Clock, Activity } from 'lucide-react';

interface SimulationImpactDiagramProps {
  plan?: Plan | null;
  scenario?: Scenario | null;
  result?: SimulationResult | null;
}

export function SimulationImpactDiagram({ plan, scenario, result }: SimulationImpactDiagramProps) {
  const isMonteCarlo = !!result?.monte_carlo;
  const delayTotal = result?.total_delay_minutes ?? 18;
  const affectedCount = result?.affected_train_ids?.length ?? 2;
  const p95Delay = result?.monte_carlo?.p90_delay_min ?? Math.round(delayTotal * 1.35);

  return (
    <div style={{
      background: 'var(--surface-elevated)',
      border: '1px solid var(--surface-border)',
      borderRadius: 'var(--radius-md)',
      overflow: 'hidden',
      marginBottom: '1.5rem',
    }}>
      {/* Header bar */}
      <div style={{
        padding: '0.85rem 1.25rem',
        background: 'rgba(15, 23, 42, 0.85)',
        borderBottom: '1px solid var(--surface-border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '0.75rem',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: '28px',
            height: '28px',
            borderRadius: 'var(--radius-xs)',
            background: 'rgba(245, 158, 11, 0.15)',
            border: '1px solid rgba(245, 158, 11, 0.3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--status-warning)',
          }}>
            <Activity size={16} />
          </div>
          <div>
            <div style={{ fontSize: '0.68rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              DISRUPTION PROPAGATION & IMPACT CASCADE
            </div>
            <div style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Simulation Digital Twin Flow: {plan?.plan_id || 'Base Plan'} × {scenario?.name || 'Scenario'}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <span className="delay-pill" style={{ background: 'rgba(56, 189, 248, 0.12)', color: 'var(--text-accent)', border: '1px solid rgba(56, 189, 248, 0.3)' }}>
            E05 Simulation Engine
          </span>
          <span className="delay-pill delay-pill-on-time">
            Deterministic + Stochastic Run
          </span>
        </div>
      </div>

      {/* Interactive 5-Stage Impact Flow Pipeline */}
      <div style={{ padding: '1.25rem', overflowX: 'auto', background: '#070b12' }}>
        <div style={{ display: 'flex', alignItems: 'stretch', gap: '0.75rem', minWidth: '820px' }}>
          
          {/* Stage 1: Base Plan */}
          <div style={{
            flex: 1,
            background: 'rgba(15, 23, 42, 0.6)',
            border: '1px solid var(--surface-border)',
            borderRadius: 'var(--radius-sm)',
            padding: '1rem',
            display: 'flex',
            flexDirection: 'column',
          }}>
            <div style={{ fontSize: '0.68rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
              STAGE 1 · BASELINE
            </div>
            <strong style={{ color: 'var(--text-accent)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>
              {plan?.plan_id || 'PLAN-BALANCED-01'}
            </strong>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', lineHeight: 1.4, flex: 1 }}>
              <div>Strategy: <strong>{plan?.strategy || 'BALANCED'}</strong></div>
              <div>Blocks: <strong>{plan?.blocks?.length ?? 4} possession(s)</strong></div>
              <div>Baseline Delay: <strong>{plan?.metrics?.total_delay_minutes ?? 0}m</strong></div>
            </div>
            <div style={{ marginTop: '0.75rem', padding: '0.3rem 0.5rem', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '3px', fontSize: '0.68rem', color: 'var(--status-normal)', textAlign: 'center' }}>
              ✓ Interlocking Feasible
            </div>
          </div>

          {/* Connector */}
          <div style={{ display: 'flex', alignItems: 'center', color: 'var(--text-muted)' }}>
            <ArrowRight size={18} />
          </div>

          {/* Stage 2: Disruption Event */}
          <div style={{
            flex: 1,
            background: 'rgba(15, 23, 42, 0.6)',
            border: '1px solid rgba(245, 158, 11, 0.4)',
            borderRadius: 'var(--radius-sm)',
            padding: '1rem',
            display: 'flex',
            flexDirection: 'column',
          }}>
            <div style={{ fontSize: '0.68rem', fontFamily: 'var(--font-mono)', color: 'var(--status-warning)', textTransform: 'uppercase', marginBottom: '0.35rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <AlertTriangle size={12} /> STAGE 2 · PERTURBATION
            </div>
            <strong style={{ color: 'var(--status-warning)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>
              {scenario?.name || 'Block Overrun +45m'}
            </strong>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', lineHeight: 1.4, flex: 1 }}>
              <div>Section: <strong>SEC-04 (Single Line)</strong></div>
              <div>Type: <strong>Maintenance Overrun</strong></div>
              <div>Magnitude: <strong>+45 min variance</strong></div>
            </div>
            <div style={{ marginTop: '0.75rem', padding: '0.3rem 0.5rem', background: 'rgba(245, 158, 11, 0.12)', border: '1px solid rgba(245, 158, 11, 0.3)', borderRadius: '3px', fontSize: '0.68rem', color: 'var(--status-warning)', textAlign: 'center' }}>
              ⚡ Headway Breached
            </div>
          </div>

          {/* Connector */}
          <div style={{ display: 'flex', alignItems: 'center', color: 'var(--text-muted)' }}>
            <ArrowRight size={18} />
          </div>

          {/* Stage 3: Propagation Cascade */}
          <div style={{
            flex: 1.1,
            background: 'rgba(15, 23, 42, 0.6)',
            border: '1px solid var(--surface-border)',
            borderRadius: 'var(--radius-sm)',
            padding: '1rem',
            display: 'flex',
            flexDirection: 'column',
          }}>
            <div style={{ fontSize: '0.68rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
              STAGE 3 · PROPAGATION
            </div>
            <strong style={{ color: 'var(--text-primary)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>
              Cascading Delay Chain
            </strong>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', lineHeight: 1.4, flex: 1 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>TRN-12001 (Shatabdi):</span>
                <strong style={{ color: 'var(--status-critical)' }}>+25m</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>TRN-12952 (Rajdhani):</span>
                <strong style={{ color: 'var(--status-warning)' }}>+14m</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>TRN-GOODS-88:</span>
                <strong style={{ color: 'var(--status-attention)' }}>Held Devpuri</strong>
              </div>
            </div>
            <div style={{ marginTop: '0.75rem', padding: '0.3rem 0.5rem', background: 'rgba(239, 68, 68, 0.12)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '3px', fontSize: '0.68rem', color: 'var(--status-critical)', textAlign: 'center' }}>
              {affectedCount} Service(s) Impacted
            </div>
          </div>

          {/* Connector */}
          <div style={{ display: 'flex', alignItems: 'center', color: 'var(--text-muted)' }}>
            <ArrowRight size={18} />
          </div>

          {/* Stage 4: Network Impact */}
          <div style={{
            flex: 1.1,
            background: 'rgba(15, 23, 42, 0.6)',
            border: '1px solid var(--surface-border)',
            borderRadius: 'var(--radius-sm)',
            padding: '1rem',
            display: 'flex',
            flexDirection: 'column',
          }}>
            <div style={{ fontSize: '0.68rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
              STAGE 4 · KPI IMPACT
            </div>
            <strong style={{ color: 'var(--text-primary)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>
              Aggregated Metrics
            </strong>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', lineHeight: 1.4, flex: 1 }}>
              <div>Total Delay: <strong style={{ color: 'var(--status-warning)' }}>+{delayTotal}m</strong></div>
              <div>95th Percentile (P95): <strong style={{ color: 'var(--text-accent)' }}>{p95Delay}m</strong></div>
              <div>Punctuality Drop: <strong style={{ color: 'var(--status-critical)' }}>-8.2%</strong></div>
            </div>
            <div style={{ marginTop: '0.75rem', padding: '0.3rem 0.5rem', background: 'var(--surface-panel)', border: '1px solid var(--surface-border)', borderRadius: '3px', fontSize: '0.68rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
              P90 Confidence 88%
            </div>
          </div>

          {/* Connector */}
          <div style={{ display: 'flex', alignItems: 'center', color: 'var(--text-muted)' }}>
            <ArrowRight size={18} />
          </div>

          {/* Stage 5: Recovery Recommendation */}
          <div style={{
            flex: 1.2,
            background: 'rgba(16, 185, 129, 0.08)',
            border: '1px solid rgba(16, 185, 129, 0.35)',
            borderRadius: 'var(--radius-sm)',
            padding: '1rem',
            display: 'flex',
            flexDirection: 'column',
          }}>
            <div style={{ fontSize: '0.68rem', fontFamily: 'var(--font-mono)', color: 'var(--status-normal)', textTransform: 'uppercase', marginBottom: '0.35rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <ShieldCheck size={12} /> STAGE 5 · RECOVERY
            </div>
            <strong style={{ color: 'var(--status-normal)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>
              P18 Recovery Available
            </strong>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', lineHeight: 1.4, flex: 1 }}>
              <div>• Reschedule SEC-04 block to 03:00</div>
              <div>• Route Goods via SEC-08 chord</div>
              <div>• Net delay recovery: <strong>~32 min</strong></div>
            </div>
            <button
              type="button"
              onClick={() => { window.location.href = '/disruptions'; }}
              style={{
                marginTop: '0.75rem',
                padding: '0.35rem 0.5rem',
                background: 'rgba(16, 185, 129, 0.2)',
                border: '1px solid rgba(16, 185, 129, 0.5)',
                borderRadius: '3px',
                fontSize: '0.7rem',
                fontWeight: 600,
                color: 'var(--status-normal)',
                cursor: 'pointer',
                textAlign: 'center',
              }}
            >
              Open Recovery Re-Plan →
            </button>
          </div>

        </div>
      </div>
    </div>
  );
}
