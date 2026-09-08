import React from 'react';

interface MetricCardProps {
  label: string;
  value: string | number;
  detail?: string;
  trend?: string;
  statusTone?: 'normal' | 'attention' | 'warning' | 'critical' | 'neutral';
  stateType?: 'PLAN' | 'ACTUAL' | 'PREDICTION' | 'SCENARIO';
}

export function MetricCard({
  label,
  value,
  detail,
  trend,
  statusTone = 'neutral'
}: MetricCardProps) {
  const getToneColor = () => {
    switch (statusTone) {
      case 'normal': return 'var(--status-normal)';
      case 'attention': return 'var(--status-attention)';
      case 'warning': return 'var(--status-warning)';
      case 'critical': return 'var(--status-critical)';
      case 'neutral':
      default: return 'var(--text-primary)';
    }
  };

  return (
    <article className="metric-kpi-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span className="kpi-label">{label}</span>
        {trend && (
          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
            {trend}
          </span>
        )}
      </div>
      <div className="kpi-value" style={{ color: getToneColor() }}>
        {value}
      </div>
      {detail && <div className="kpi-detail">{detail}</div>}
    </article>
  );
}
