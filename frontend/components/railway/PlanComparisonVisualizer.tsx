'use client';

import React from 'react';
import { BarChart3, TrendingDown, Clock, ShieldCheck, CheckCircle2, Layers } from 'lucide-react';

interface PlanCandidate {
  planId: string;
  planName: string;
  strategy: string;
  metrics: {
    total_delay_minutes: number;
    passenger_trains_affected: number;
    goods_trains_affected: number;
    maintenance_tasks_completed: number;
    maintenance_tasks_unscheduled: number;
    blocks_count: number;
    overall_overrun_risk: number;
  };
}

interface PlanComparisonVisualizerProps {
  candidates: PlanCandidate[];
  recommendedPlanId?: string;
  tradeoffSummary?: string[];
}

export function PlanComparisonVisualizer({
  candidates,
  recommendedPlanId,
  tradeoffSummary = [],
}: PlanComparisonVisualizerProps) {
  if (!candidates || candidates.length === 0) return null;

  // Find max values for normalized bars
  const maxDelay = Math.max(...candidates.map(c => c.metrics.total_delay_minutes), 1);
  const maxTasks = Math.max(...candidates.map(c => c.metrics.maintenance_tasks_completed), 1);

  return (
    <div style={{
      background: 'var(--surface-elevated)',
      border: '1px solid var(--surface-border)',
      borderRadius: 'var(--radius-md)',
      overflow: 'hidden',
      marginBottom: '1.5rem',
    }}>
      {/* Header */}
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
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--status-normal)',
          }}>
            <BarChart3 size={16} />
          </div>
          <div>
            <div style={{ fontSize: '0.68rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              MULTI-CRITERIA TRADE-OFF RADAR
            </div>
            <div style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Candidate Plan Benchmarks ({candidates.length} Alternatives)
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <span className="delay-pill" style={{ background: 'rgba(16, 185, 129, 0.12)', color: 'var(--status-normal)', border: '1px solid rgba(16, 185, 129, 0.4)' }}>
            ✓ Recommended: {recommendedPlanId || candidates[0]?.planId}
          </span>
        </div>
      </div>

      {/* Comparative Cards Grid */}
      <div style={{ padding: '1.25rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
        {candidates.map((cand) => {
          const isRecommended = cand.planId === recommendedPlanId || (!recommendedPlanId && cand === candidates[0]);
          const delayPct = Math.round((cand.metrics.total_delay_minutes / maxDelay) * 100);
          const tasksPct = Math.round((cand.metrics.maintenance_tasks_completed / maxTasks) * 100);
          const riskPct = Math.round((cand.metrics.overall_overrun_risk || 0.15) * 100);

          return (
            <div
              key={cand.planId}
              style={{
                background: isRecommended ? 'rgba(16, 185, 129, 0.05)' : 'var(--surface-panel)',
                border: `1.5px solid ${isRecommended ? 'rgba(16, 185, 129, 0.4)' : 'var(--surface-border)'}`,
                borderRadius: 'var(--radius-sm)',
                padding: '1rem',
                display: 'flex',
                flexDirection: 'column',
                position: 'relative',
              }}
            >
              {isRecommended && (
                <div style={{
                  position: 'absolute',
                  top: '0.75rem',
                  right: '0.75rem',
                  fontSize: '0.65rem',
                  fontWeight: 700,
                  color: 'var(--status-normal)',
                  background: 'rgba(16, 185, 129, 0.15)',
                  padding: '2px 6px',
                  borderRadius: '3px',
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                }}>
                  ★ RECOMMENDED
                </div>
              )}

              <div style={{ fontSize: '0.7rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                {cand.strategy}
              </div>
              <strong style={{ fontSize: '1rem', color: isRecommended ? 'var(--status-normal)' : 'var(--text-primary)', marginBottom: '0.75rem' }}>
                {cand.planId}
              </strong>

              {/* Metric 1: Train Delay */}
              <div style={{ marginBottom: '0.75rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '0.25rem' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Total Delay</span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: cand.metrics.total_delay_minutes <= 15 ? 'var(--status-normal)' : 'var(--status-warning)' }}>
                    +{cand.metrics.total_delay_minutes} min
                  </span>
                </div>
                <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.06)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${delayPct}%`,
                    height: '100%',
                    background: cand.metrics.total_delay_minutes <= 15 ? 'var(--status-normal)' : 'var(--status-warning)',
                    borderRadius: '3px',
                  }} />
                </div>
              </div>

              {/* Metric 2: Completed Backlog */}
              <div style={{ marginBottom: '0.75rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '0.25rem' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Tasks Completed</span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--text-accent)' }}>
                    {cand.metrics.maintenance_tasks_completed} tasks
                  </span>
                </div>
                <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.06)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${tasksPct}%`,
                    height: '100%',
                    background: 'var(--text-accent)',
                    borderRadius: '3px',
                  }} />
                </div>
              </div>

              {/* Metric 3: Overrun Exposure Risk */}
              <div style={{ marginBottom: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '0.25rem' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Overrun Exposure</span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: riskPct <= 20 ? 'var(--status-normal)' : 'var(--status-critical)' }}>
                    {riskPct}% risk
                  </span>
                </div>
                <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.06)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${riskPct}%`,
                    height: '100%',
                    background: riskPct <= 20 ? 'var(--status-normal)' : 'var(--status-critical)',
                    borderRadius: '3px',
                  }} />
                </div>
              </div>

              {/* Action Button */}
              <button
                type="button"
                onClick={() => { window.location.href = `/simulation?planId=${cand.planId}`; }}
                style={{
                  marginTop: 'auto',
                  padding: '0.45rem',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  borderRadius: 'var(--radius-xs)',
                  border: '1px solid var(--surface-border)',
                  background: 'var(--surface-elevated)',
                  color: 'var(--text-primary)',
                  cursor: 'pointer',
                  textAlign: 'center',
                }}
              >
                Simulate this candidate →
              </button>
            </div>
          );
        })}
      </div>

      {/* Trade-off summary footer */}
      {tradeoffSummary.length > 0 && (
        <div style={{
          padding: '0.75rem 1.25rem',
          background: 'rgba(15, 23, 42, 0.6)',
          borderTop: '1px solid var(--surface-border)',
          fontSize: '0.75rem',
          color: 'var(--text-secondary)',
        }}>
          <strong style={{ color: 'var(--text-primary)', marginRight: '0.5rem' }}>AI Decision Intelligence (P17):</strong>
          {tradeoffSummary.join(' · ')}
        </div>
      )}
    </div>
  );
}
