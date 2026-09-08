'use client';

import React from 'react';
import Link from 'next/link';
import { ErrorState, LoadingState } from '../feedback/FeedbackStates';
import type { SectionSnapshot, SectionStatus } from '../../hooks/useCommandCenterData';

interface SectionCardProps {
  eyebrow: string;
  title: string;
  status: SectionStatus;
  errorMessage?: string | null;
  onRetry?: () => void;
  href?: string;
  hrefLabel?: string;
  badge?: React.ReactNode;
  children: React.ReactNode;
  bodyPadding?: 'none' | 'sm' | 'md';
  testId?: string;
}

export function SectionCard({
  eyebrow,
  title,
  status,
  errorMessage,
  onRetry,
  href,
  hrefLabel,
  badge,
  children,
  bodyPadding = 'md',
  testId,
}: SectionCardProps) {
  const statusLabel = status === 'loading'
    ? 'LOADING'
    : status === 'error'
      ? 'ERROR'
      : status === 'success'
        ? 'LIVE'
        : 'IDLE';

  const statusClass = status === 'success'
    ? 'cc-status-dot cc-status-live'
    : status === 'error'
      ? 'cc-status-dot cc-status-error'
      : status === 'loading'
        ? 'cc-status-dot cc-status-loading'
        : 'cc-status-dot';

  return (
    <section className="cc-section-card" aria-labelledby={`cc-section-${title}`} data-testid={testId}>
      <header className="cc-section-header">
        <div>
          <span className="cc-section-eyebrow">{eyebrow}</span>
          <h2 id={`cc-section-${title}`} className="cc-section-title">{title}</h2>
       </div>
        <div className="cc-section-meta">
          {badge}
          <span
            className={statusClass}
            aria-label={`Section status: ${statusLabel}`}
            title={statusLabel}
          >
            <span aria-hidden="true" className="cc-status-glyph">●</span>
            <span className="cc-status-label">{statusLabel}</span>
         </span>
          {href && (
            <Link href={href} className="cc-section-link" aria-label={hrefLabel ?? `Open ${title}`}>
              {hrefLabel ?? 'Open'} →
           </Link>
          )}
       </div>
     </header>

      <div className={`cc-section-body cc-body-${bodyPadding}`}>
        {status === 'loading' ? (
          <LoadingState message={`Loading ${title.toLowerCase()}…`} />
        ) : status === 'error' ? (
          <ErrorState
            title={`${title} unavailable`}
            error={errorMessage ?? 'Section data could not be loaded.'}
            affectedScope="This dashboard section"
            onRetry={onRetry}
          />
        ) : (
          children
        )}
     </div>
   </section>
  );
}

export function SnapshotReady<T>({
  snapshot,
  render,
}: {
  snapshot: SectionSnapshot<T>;
  render: (data: NonNullable<T>) => React.ReactNode;
}): React.ReactElement | null {
  if (snapshot.status !== 'success' || snapshot.data === null || snapshot.data === undefined) {
    return null;
  }
  return <>{render(snapshot.data as NonNullable<T>)}</>;
}
