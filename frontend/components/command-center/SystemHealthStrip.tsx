'use client';

import React from 'react';
import type { SectionSnapshot } from '../../hooks/useCommandCenterData';
import { RailmindApiError } from '../../services/api/client/errors';

interface SystemHealthStripProps {
  snapshot: SectionSnapshot<{ healthy: boolean; version: string | null }>;
}

export function SystemHealthStrip({ snapshot }: SystemHealthStripProps) {
  const healthy = snapshot.status === 'success' && snapshot.data?.healthy === true;
  const version = snapshot.data?.version ?? null;
  const source: 'REAL' | 'MOCK' | 'UNKNOWN' = snapshot.source;

  return (
    <section className="cc-health-strip" aria-label="Backend health">
      <div className="cc-health-item">
        <span className="cc-health-label">RailMind API</span>
        <HealthBadge
          status={
            healthy ? 'UP' : snapshot.status === 'loading' ? 'CHECKING' : 'DOWN'
          }
        />
        {version && (
          <span className="cc-health-meta" aria-label={`API version ${version}`}>
            v{version}
         </span>
        )}
        {snapshot.status === 'error' && snapshot.error && (
          <span className="cc-health-meta" title={describeError(snapshot.error)}>
            {snapshot.errorMessage}
         </span>
        )}
     </div>
      <div className="cc-health-item">
        <span className="cc-health-label">Data Source</span>
        <span className={`cc-source-pill cc-source-${source.toLowerCase()}`} title={describeSource(source, snapshot.error)}>
          {source}
       </span>
     </div>
   </section>
  );
}

function HealthBadge({ status }: { status: 'UP' | 'DOWN' | 'CHECKING' }) {
  const cls =
    status === 'UP'
      ? 'cc-health-badge cc-health-up'
      : status === 'DOWN'
        ? 'cc-health-badge cc-health-down'
        : 'cc-health-badge cc-health-checking';
  const label = status === 'UP' ? '● Healthy' : status === 'DOWN' ? '● Unavailable' : '● Checking…';
  return <span className={cls} role="status">{label}</span>;
}

function describeSource(source: 'REAL' | 'MOCK' | 'UNKNOWN', error: RailmindApiError | null): string {
  if (source === 'REAL') return 'Data is sourced from the FastAPI backend.';
  if (source === 'MOCK') return 'Data is from the deterministic mock fixtures (no backend).';
  if (error) return `Provenance unknown: ${error.kind} error while probing.`;
  return 'Provenance could not be determined.';
}

function describeError(error: RailmindApiError): string {
  return `${error.kind}: ${error.message}`;
}
