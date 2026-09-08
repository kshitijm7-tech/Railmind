import React from 'react';
import { Button } from '../ui/Button';

export function LoadingState({ message = 'Loading operational telemetry...' }: { message?: string }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
      <div style={{ width: '28px', height: '28px', border: '3px solid var(--surface-border)', borderTopColor: 'var(--text-accent)', borderRadius: '50%', animation: 'spin 1s linear infinite', marginBottom: '1rem' }} />
      <p style={{ margin: 0, fontSize: '0.85rem' }}>{message}</p>
      <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

export function EmptyState({
  title = 'No records available',
  description = 'No active items match the current corridor filters.',
  actionLabel,
  onAction
}: {
  title?: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '3.5rem 2rem', background: 'var(--surface-panel)', border: '1px solid var(--surface-border)', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
      <div style={{ fontSize: '2rem', marginBottom: '0.75rem', opacity: 0.6 }}>📋</div>
      <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1rem', color: 'var(--text-primary)' }}>{title}</h3>
      <p style={{ margin: '0 0 1.25rem 0', color: 'var(--text-secondary)', fontSize: '0.82rem', maxWidth: '28rem' }}>{description}</p>
      {actionLabel && onAction && (
        <Button variant="secondary" size="sm" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
}

export function ErrorState({
  title = 'Operational Engine Error',
  error,
  affectedScope = 'Local Corridor View',
  onRetry
}: {
  title?: string;
  error?: string;
  affectedScope?: string;
  onRetry?: () => void;
}) {
  return (
    <div style={{ padding: '1.5rem', background: 'var(--status-critical-bg)', border: '1px solid var(--status-critical)', borderRadius: 'var(--radius-md)' }} role="alert">
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
        <span style={{ fontSize: '1.5rem' }}>⚠️</span>
        <div style={{ flex: 1 }}>
          <h4 style={{ margin: '0 0 0.35rem 0', color: 'var(--status-critical)', fontSize: '0.95rem' }}>{title}</h4>
          <p style={{ margin: '0 0 0.5rem 0', color: 'var(--text-primary)', fontSize: '0.82rem' }}>
            {error || 'An unexpected operational discrepancy occurred. Live safety state remains uncompromised.'}
          </p>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
            <strong>Affected Scope: </strong>{affectedScope} · Safety interlocks active
          </div>
        </div>
        {onRetry && (
          <Button variant="danger" size="sm" onClick={onRetry}>
            Retry Request
          </Button>
        )}
      </div>
    </div>
  );
}

export function ComputeState({
  status,
  details
}: {
  status: 'Preparing' | 'Optimizing' | 'Simulating' | 'Evaluating' | 'Completed' | 'Failed';
  details?: string;
}) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '1rem 1.5rem', background: 'var(--surface-elevated)', border: '1px solid var(--surface-border)', borderRadius: 'var(--radius-md)' }}>
      <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: status === 'Completed' ? 'var(--status-approved)' : status === 'Failed' ? 'var(--status-critical)' : 'var(--text-accent)', animation: status !== 'Completed' && status !== 'Failed' ? 'pulse 1.5s infinite' : 'none' }} />
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>
          CP-SAT Engine Status: {status}
        </div>
        {details && <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{details}</div>}
      </div>
      <style>{`@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }`}</style>
    </div>
  );
}
