'use client';

import React from 'react';
import { MetricCard } from '../operational/MetricCard';

interface MaintenanceKPIsProps {
  kpis: {
    critical: number;
    high: number;
    overdue: number;
    dueSoon: number;
    open: number;
    inProgress: number;
    completed: number;
    total: number;
  };
}

export function MaintenanceKPIs({ kpis }: MaintenanceKPIsProps) {
  return (
    <div className="maintenance-kpi-row" aria-label="Maintenance key metrics">
      <MetricCard label="Critical" value={kpis.critical} statusTone="critical" />
      <MetricCard label="High" value={kpis.high} statusTone="warning" />
      <MetricCard label="Overdue" value={kpis.overdue} statusTone="critical" />
      <MetricCard label="Due Soon" value={kpis.dueSoon} statusTone="warning" />
      <MetricCard label="Open" value={kpis.open} statusTone="attention" />
      <MetricCard label="In Progress" value={kpis.inProgress} statusTone="attention" />
      <MetricCard label="Completed" value={kpis.completed} statusTone="normal" />
      <MetricCard label="Total" value={kpis.total} statusTone="neutral" />
    </div>
  );
}