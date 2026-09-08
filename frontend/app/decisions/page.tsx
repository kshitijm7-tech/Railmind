'use client';

import React, { useEffect, useState } from 'react';
import { AppShell } from '../../components/layout/AppShell';
import { DecisionCard } from '../../components/decision/DecisionCard';
import { StateBadge } from '../../components/state/StateBadge';
import { services } from '../../services';
import { Recommendation, DecisionRecord } from '../../domain';

export default function DecisionsPage() {
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [history, setHistory] = useState<DecisionRecord[]>([]);

  useEffect(() => {
    services.recommendations.getLatestRecommendation().then(setRecommendation);
    services.decisions.getDecisionHistory().then(setHistory);
  }, []);

  const handleApprove = async (id: string) => {
    const record = await services.decisions.submitDecision({
      recommendation_id: id,
      plan_id: recommendation?.plan_id || '',
      state_version: recommendation?.state_version || 'v1024',
      action: 'APPROVE',
      authorized_by: 'Senior Operations Controller',
      user_role: 'Operations Controller',
      notes: 'Approved via Decisions workspace review.'
    });
    setHistory(prev => [record, ...prev]);
    alert('Decision recorded in immutable audit log.');
  };

  return (
    <AppShell
      title="Decisions & Human-in-the-Loop Approvals"
      eyebrow="Governance & Authorization Gate"
      actions={<StateBadge stateType="PREDICTION" label="HUMAN AUTHORIZATION REQUIRED" />}
    >
      <div style={{ marginBottom: '1.5rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
        AI recommends; authorized railway operators verify mathematical evidence and approve or modify operational plans.
      </div>

      <div style={{ marginBottom: '2rem' }}>
        <h3 style={{ margin: '0 0 0.75rem 0', fontSize: '1.05rem' }}>Pending Recommendations Queue</h3>
        {recommendation ? (
          <DecisionCard
            recommendation={recommendation}
            onApprove={handleApprove}
            onModify={() => alert('Modify parameters modal (Phase 5)')}
            onReject={() => alert('Recommendation rejected')}
          />
        ) : (
          <div style={{ padding: '1.5rem', background: 'var(--surface-panel)', border: '1px solid var(--surface-border)', borderRadius: 'var(--radius-md)', textAlign: 'center', color: 'var(--text-muted)' }}>
            No recommendations currently awaiting approval.
          </div>
        )}
      </div>

      <div>
        <h3 style={{ margin: '0 0 0.75rem 0', fontSize: '1.05rem' }}>Decision Audit History (This Session)</h3>
        {history.length === 0 ? (
          <div style={{ padding: '1rem', background: 'var(--surface-panel)', border: '1px solid var(--surface-border)', borderRadius: 'var(--radius-md)', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
            No authorization actions submitted yet during this session.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {history.map(d => (
              <div key={d.decision_id} style={{ padding: '0.75rem 1rem', background: 'var(--surface-panel)', border: '1px solid var(--status-approved)', borderRadius: 'var(--radius-sm)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <strong style={{ color: '#22c55e', marginRight: '0.5rem' }}>✓ {d.action}</strong>
                  <span style={{ fontSize: '0.82rem', color: 'var(--text-primary)' }}>Plan {d.plan_id}</span>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Authorized by: {d.authorized_by} ({d.user_role})</div>
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                  {new Date(d.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}
