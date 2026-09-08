'use client';

import React from 'react';

export type AlertSeverity = 'CRITICAL' | 'WARNING' | 'INFO';

export interface CommandCenterAlert {
  id: string;
  severity: AlertSeverity;
  title: string;
  detail: string;
  source: string;
  href?: string;
}

interface AlertsListProps {
  alerts: CommandCenterAlert[];
}

const severityOrder: Record<AlertSeverity, number> = {
  CRITICAL: 0,
  WARNING: 1,
  INFO: 2,
};

export function AlertsList({ alerts }: AlertsListProps) {
  if (alerts.length === 0) {
    return (
      <div className="cc-alerts-empty" role="status">
        <span className="cc-alerts-empty-icon" aria-hidden="true">●</span>
        <div>
          <strong>All clear</strong>
          <p>No operational issues currently require human attention</p>
      </div>
    </div>
    );
  }

  const sorted = [...alerts].sort(
    (a, b) => severityOrder[a.severity] - severityOrder[b.severity],
  );

  return (
    <ul className="cc-alerts-list" aria-label="Operational alerts">
      {sorted.map((alert) => (
        <li
          key={alert.id}
          className={`cc-alert cc-alert-${alert.severity.toLowerCase()}`}
        >
          <span className="cc-alert-glyph" aria-hidden="true">
            {alert.severity === 'CRITICAL' ? '\u2715' : alert.severity === 'WARNING' ? '\u26a0' : '\u24d8'}
        </span>
          <div className="cc-alert-body">
            <div className="cc-alert-head">
              <span className={`cc-alert-tag cc-alert-tag-${alert.severity.toLowerCase()}`}>
                {alert.severity}
            </span>
              <strong className="cc-alert-title">{alert.title}</strong>
          </div>
            <p className="cc-alert-detail">{alert.detail}</p>
            <span className="cc-alert-source">Source: {alert.source}</span>
        </div>
          {alert.href && (
            <a className="cc-alert-link" href={alert.href}>
              Open →
          </a>
          )}
      </li>
      ))}
  </ul>
  );
}
