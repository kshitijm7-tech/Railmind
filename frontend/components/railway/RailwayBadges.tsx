import React from 'react';
import { Department, Criticality, TrainType } from '../../domain';

export function DepartmentBadge({ department }: { department: Department }) {
  const getStyle = (): React.CSSProperties => {
    switch (department) {
      case 'Engineering':
        return { background: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa', border: '1px solid rgba(59, 130, 246, 0.4)' };
      case 'S&T':
        return { background: 'rgba(139, 92, 246, 0.15)', color: '#c084fc', border: '1px solid rgba(139, 92, 246, 0.4)' };
      case 'TRD':
        return { background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24', border: '1px solid rgba(245, 158, 11, 0.4)' };
      case 'OHE':
        return { background: 'rgba(6, 182, 212, 0.15)', color: '#22d3ee', border: '1px solid rgba(6, 182, 212, 0.4)' };
    }
  };

  return (
    <span
      style={{
        ...getStyle(),
        display: 'inline-flex',
        alignItems: 'center',
        padding: '0.15rem 0.45rem',
        borderRadius: 'var(--radius-xs)',
        fontSize: '0.7rem',
        fontWeight: 600,
        fontFamily: 'var(--font-mono)',
        whiteSpace: 'nowrap'
      }}
    >
      {department}
    </span>
  );
}

export function CriticalityBadge({ criticality }: { criticality: Criticality }) {
  const getStyle = (): React.CSSProperties => {
    switch (criticality) {
      case 'CRITICAL':
        return { background: 'var(--status-critical-bg)', color: 'var(--status-critical)', border: '1px solid var(--status-critical)' };
      case 'HIGH':
        return { background: 'var(--status-warning-bg)', color: 'var(--status-warning)', border: '1px solid var(--status-warning)' };
      case 'MEDIUM':
        return { background: 'var(--status-attention-bg)', color: 'var(--status-attention)', border: '1px solid var(--status-attention)' };
      case 'LOW':
      default:
        return { background: 'rgba(148, 163, 184, 0.12)', color: '#94a3b8', border: '1px solid rgba(148, 163, 184, 0.3)' };
    }
  };

  return (
    <span
      style={{
        ...getStyle(),
        display: 'inline-flex',
        alignItems: 'center',
        padding: '0.15rem 0.45rem',
        borderRadius: 'var(--radius-xs)',
        fontSize: '0.68rem',
        fontWeight: 700,
        letterSpacing: '0.04em',
        textTransform: 'uppercase'
      }}
    >
      {criticality}
    </span>
  );
}

export function TrainBadge({
  trainNumber,
  trainType,
  priority
}: {
  trainNumber: string;
  trainType: TrainType;
  priority?: number;
}) {
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.35rem',
        background: 'var(--surface-elevated)',
        border: '1px solid var(--surface-border)',
        padding: '0.2rem 0.5rem',
        borderRadius: 'var(--radius-xs)',
        fontSize: '0.75rem',
        fontFamily: 'var(--font-mono)'
      }}
    >
      <span style={{ color: trainType === 'Passenger' ? '#38bdf8' : '#f59e0b', fontWeight: 700 }}>
        {trainType === 'Passenger' ? '🚆' : '🚂'} {trainNumber}
      </span>
      {priority !== undefined && (
        <span style={{ color: 'var(--text-muted)', fontSize: '0.68rem' }} title={`Priority Rank ${priority}`}>
          (P{priority})
        </span>
      )}
    </span>
  );
}

export function SectionBadge({ sectionId }: { sectionId: string }) {
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        background: 'rgba(30, 58, 80, 0.5)',
        border: '1px solid var(--surface-border)',
        color: '#bae6fd',
        padding: '0.15rem 0.45rem',
        borderRadius: 'var(--radius-xs)',
        fontSize: '0.72rem',
        fontFamily: 'var(--font-mono)',
        fontWeight: 600
      }}
    >
      📍 {sectionId}
    </span>
  );
}
