'use client';

import React, { useEffect, useState } from 'react';
import { AppShell } from '../../components/layout/AppShell';
import { DataTable, ColumnDef } from '../../components/operational/DataTable';
import { SectionBadge, DepartmentBadge, CriticalityBadge } from '../../components/railway/RailwayBadges';
import { StateBadge } from '../../components/state/StateBadge';
import { services } from '../../services';
import { MaintenanceTask } from '../../domain';

export default function MaintenancePage() {
  const [tasks, setTasks] = useState<MaintenanceTask[]>([]);

  useEffect(() => {
    services.maintenance.getTasks().then(setTasks);
  }, []);

  const columns: ColumnDef<MaintenanceTask>[] = [
    { header: 'Task ID', cell: (t) => <strong style={{ fontFamily: 'var(--font-mono)' }}>{t.task_id}</strong> },
    { header: 'Title', accessorKey: 'title' },
    { header: 'Section', cell: (t) => <SectionBadge sectionId={t.section_id} /> },
    { header: 'Dept', cell: (t) => <DepartmentBadge department={t.department} /> },
    { header: 'Type', accessorKey: 'task_type' },
    { header: 'Est. Duration', cell: (t) => `${t.expected_duration_min} min (P90: ${t.duration_estimates.p90_min}m)` },
    { header: 'Crew Req.', cell: (t) => `${t.crew_size_required} (${t.crew_qualification})` },
    { header: 'Criticality', cell: (t) => <CriticalityBadge criticality={t.criticality} /> },
    { header: 'Overdue', cell: (t) => t.overdue_days > 0 ? <span style={{ color: '#ef4444', fontWeight: 700 }}>+{t.overdue_days} days</span> : 'On Schedule' },
    { header: 'Priority Score', cell: (t) => <strong style={{ fontFamily: 'var(--font-mono)', color: t.priority_score > 90 ? '#ef4444' : '#38bdf8' }}>{t.priority_score.toFixed(1)}</strong> }
  ];

  return (
    <AppShell
      title="Maintenance Intelligence & Backlog"
      eyebrow="Prioritization & Possession Demand"
      actions={<StateBadge stateType="PREDICTION" label="EXPLAINABLE PRIORITY SCORED" />}
    >
      <div style={{ marginBottom: '1.25rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
        Maintenance demand across Engineering, S&T, TRD, and OHE departments scored via explainable factors.
      </div>
      <DataTable
        columns={columns}
        data={tasks}
        keyExtractor={(t) => t.task_id}
      />
    </AppShell>
  );
}
