'use client';

import React, { useState } from 'react';
import { Recommendation } from '../../domain';
import { StateBadge } from '../state/StateBadge';
import { ObjectiveBreakdownView, ConstraintTraceView } from '../operational/EvidenceViews';
import { Button } from '../ui/Button';

interface DecisionCardProps {
  recommendation: Recommendation;
  onApprove?: (id: string) => void;
  onModify?: (id: string) => void;
  onReject?: (id: string) => void;
  isReadOnly?: boolean;
}

export function DecisionCard({
  recommendation,
  onApprove,
  onModify,
  onReject,
  isReadOnly = false
}: DecisionCardProps) {
  const [showFullEvidence, setShowFullEvidence] = useState(false);

  return (
    <article className="decision-card-container" aria-labelledby="rec-headline">
      <header className="decision-card-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
            <StateBadge stateType="PREDICTION" label="OPTIMIZED RECOMMENDATION" />
            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              State: {recommendation.state_version} · Engine: {recommendation.model_version}
            </span>
          </div>
          <h3 id="rec-headline" style={{ margin: '0.25rem 0', fontSize: '1.15rem', color: 'var(--text-primary)' }}>
            {recommendation.headline}
          </h3>
          <p style={{ margin: '0.25rem 0 0 0', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            {recommendation.action_summary}
          </p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--status-attention)', fontWeight: 600 }}>
            Structured Evidence Attached
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            Human Authorization Required
          </div>
        </div>
      </header>

      <dl className="decision-evidence-grid">
        <div className="evidence-box">
          <dt>Primary Rationale (Why this plan)</dt>
          <dd>{recommendation.primary_rationale}</dd>
        </div>

        <div className="evidence-box">
          <dt>Expected Operational Impact</dt>
          <dd>
            <strong style={{ color: '#38bdf8' }}>+{recommendation.expected_outcome.total_delay_min} min</strong> train delay across{' '}
            {recommendation.expected_outcome.affected_trains_count} train(s) ·{' '}
            <strong style={{ color: '#34d399' }}>{recommendation.expected_outcome.maintenance_completion_pct}%</strong> backlog cleared
          </dd>
        </div>

        <div className="evidence-box">
          <dt>Risk & Robustness (Monte Carlo P90)</dt>
          <dd>
            Overrun risk: <strong style={{ color: recommendation.expected_outcome.overrun_risk_pct > 20 ? '#ef4444' : '#f59e0b' }}>
              {recommendation.expected_outcome.overrun_risk_pct}%
            </strong> · Buffer window evaluated
          </dd>
        </div>

        <div className="evidence-box">
          <dt>Evaluated Alternatives ({recommendation.alternatives.length})</dt>
          <dd>
            {recommendation.alternatives.map(alt => (
              <span key={alt.plan_id} style={{ display: 'block', fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                • <strong>{alt.name}</strong> ({alt.strategy}): {alt.delay_delta_min > 0 ? `+${alt.delay_delta_min}` : alt.delay_delta_min}m delay, {alt.risk_delta_pct > 0 ? `+${alt.risk_delta_pct}` : alt.risk_delta_pct}% risk
              </span>
            ))}
          </dd>
        </div>
      </dl>

      {showFullEvidence && (
        <div style={{ padding: 'var(--spacing-5)', borderTop: '1px solid var(--surface-border)', display: 'flex', flexDirection: 'column', gap: '1.25rem', background: 'var(--surface-base)' }}>
          <ObjectiveBreakdownView terms={recommendation.objective_breakdown} />
          <ConstraintTraceView items={recommendation.constraint_trace} />
        </div>
      )}

      <footer style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: 'var(--spacing-3) var(--spacing-5)', background: 'var(--surface-panel)', borderTop: '1px solid var(--surface-border)' }}>
        <button
          type="button"
          onClick={() => setShowFullEvidence(!showFullEvidence)}
          style={{ background: 'none', border: 'none', color: 'var(--text-accent)', fontSize: '0.78rem', cursor: 'pointer', padding: 0 }}
        >
          {showFullEvidence ? '▲ Hide solver breakdown' : '▼ Inspect mathematical breakdown & constraint trace'}
        </button>

        {!isReadOnly && (
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <Button
              variant="primary"
              size="sm"
              onClick={() => onApprove && onApprove(recommendation.recommendation_id)}
            >
              ✓ Authorize & Approve Plan
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => onModify && onModify(recommendation.recommendation_id)}
            >
              ✎ Modify Parameters
            </Button>
            <Button
              variant="danger"
              size="sm"
              onClick={() => onReject && onReject(recommendation.recommendation_id)}
            >
              ✕ Reject
            </Button>
          </div>
        )}
      </footer>
    </article>
  );
}
