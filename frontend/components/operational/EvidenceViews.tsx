import React from 'react';
import { ObjectiveTerm, ConstraintTraceItem } from '../../domain';

export function ObjectiveBreakdownView({ terms }: { terms: ObjectiveTerm[] }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
        CP-SAT Objective Function Decomposition
      </h4>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.5rem' }}>
        {terms.map((term, idx) => (
          <div
            key={idx}
            style={{
              background: 'var(--surface-elevated)',
              border: '1px solid var(--surface-border)',
              borderRadius: 'var(--radius-sm)',
              padding: '0.6rem 0.8rem'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
              <span style={{ color: 'var(--text-muted)' }}>{term.name}</span>
              <strong style={{ fontFamily: 'var(--font-mono)', color: term.weighted_contribution > 0 ? '#f87171' : '#34d399' }}>
                {term.weighted_contribution > 0 ? `+${term.weighted_contribution}` : term.weighted_contribution}
              </strong>
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
              {term.description}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function ConstraintTraceView({ items }: { items: ConstraintTraceItem[] }) {
  const getStatusColor = (status: ConstraintTraceItem['status']) => {
    switch (status) {
      case 'SATISFIED': return 'var(--status-approved)';
      case 'TIGHT': return 'var(--status-warning)';
      case 'VIOLATED': return 'var(--status-critical)';
      case 'RELAXED': return 'var(--status-attention)';
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
        Active Constraint Verification & Safety Trace
      </h4>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
        {items.map((item, idx) => (
          <div
            key={idx}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              background: 'var(--surface-elevated)',
              border: '1px solid var(--surface-border)',
              borderRadius: 'var(--radius-sm)',
              padding: '0.5rem 0.75rem',
              fontSize: '0.78rem'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ color: getStatusColor(item.status), fontWeight: 700 }}>
                {item.status === 'SATISFIED' ? '✓' : item.status === 'TIGHT' ? '⚠' : '✗'}
              </span>
              <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{item.constraint_name}</span>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>({item.category})</span>
            </div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem' }}>
              {item.details}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
