'use client';

import React from 'react';
import { DataTable, ColumnDef } from '../operational/DataTable';
import { SectionBadge, DepartmentBadge, CriticalityBadge } from '../railway/RailwayBadges';
import type { MaintenanceTask } from '../../domain';
import type { DueStateFilter } from '../../hooks/useMaintenanceWorkspace';

function getDueState(task: MaintenanceTask): DueStateFilter {
  if (task.overdue_days > 0) return 'Overdue';
  if (!task.latest_finish) return 'No Deadline';
  const finish = new Date(task.latest_finish);
  const now = new Date();
  const diffDays = Math.ceil((finish.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
  if (diffDays < 0) return 'Overdue';
  if (diffDays === 0) return 'Due Today';
  if (diffDays <= 3) return 'Due Soon';
  return 'Upcoming';
}

function getDueStateLabel(task: MaintenanceTask): string {
  const state = getDueState(task);
  switch (state) {
    case 'Overdue':
      return `Overdue ${task.overdue_days}d`;
    case 'Due Today':
      return 'Due Today';
    case 'Due Soon':
      return `Due in ${task.latest_finish ? Math.ceil((new Date(task.latest_finish).getTime() - Date.now()) / (1000 * 60 * 60 * 24)) : '?'}d`;
    case 'Upcoming':
      return task.latest_finish ? new Date(task.latest_finish).toLocaleDateString() : 'Upcoming';
    case 'No Deadline':
    default:
      return 'No deadline';
  }
}

function getDueStateColor(task: MaintenanceTask): string {
  const state = getDueState(task);
  switch (state) {
    case 'Overdue':
      return 'var(--status-critical)';
    case 'Due Today':
      return 'var(--status-warning)';
    case 'Due Soon':
      return 'var(--status-attention)';
    case 'Upcoming':
      return 'var(--text-secondary)';
    case 'No Deadline':
    default:
      return 'var(--text-muted)';
  }
}

export function MaintenanceTaskTable({
  tasks,
  onRowClick,
  selectedTaskId,
}: {
  tasks: MaintenanceTask[];
  onRowClick?: (task: MaintenanceTask) => void;
  selectedTaskId: string | null;
}) {
  const columns: ColumnDef<MaintenanceTask>[] = [
    {
      header: 'Task ID',
      cell: (t) => (
        <strong style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{t.task_id}</strong>
      ),
    },
    {
      header: 'Title',
      cell: (t) => (
        <div style={{ maxWidth: '280px', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
          <strong>{t.title}</strong>
          {t.asset_id && <span style={{ marginLeft: '0.5rem', color: 'var(--text-muted)', fontSize: '0.75rem' }}>[{t.asset_id}]</span>}
        </div>
      ),
    },
    {
      header: 'Section',
      cell: (t) => <SectionBadge sectionId={t.section_id} />,
    },
    {
      header: 'Dept',
      cell: (t) => <DepartmentBadge department={t.department} />,
    },
    {
      header: 'Type',
      accessorKey: 'task_type',
    },
    {
      header: 'Priority',
      cell: (t) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <CriticalityBadge criticality={t.criticality} />
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
            {t.priority_score.toFixed(1)}
          </span>
        </div>
      ),
    },
    {
      header: 'Status',
      cell: (t) => (
        <span style={{
          fontSize: '0.75rem',
          fontWeight: 600,
          color: t.status === 'Completed' ? 'var(--status-normal)' :
                 t.status === 'In Progress' ? 'var(--status-attention)' :
                 t.status === 'Overdue' || t.status === 'Blocked' ? 'var(--status-critical)' :
                 'var(--text-secondary)',
          textTransform: 'uppercase',
          letterSpacing: '0.04em',
        }}>
          {t.status}
        </span>
      ),
    },
    {
      header: 'Due',
      cell: (t) => (
        <span style={{ color: getDueStateColor(t), fontSize: '0.75rem', fontWeight: 500 }}>
          {getDueStateLabel(t)}
        </span>
      ),
    },
    {
      header: 'Est. Duration',
      cell: (t) => `${t.expected_duration_min} min (P90: ${t.duration_estimates.p90_min}m)`,
    },
    {
      header: 'Overdue',
      cell: (t) => t.overdue_days > 0 ? (
        <span style={{ color: 'var(--status-critical)', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
          +{t.overdue_days}d
        </span>
      ) : (
        <span style={{ color: 'var(--text-muted)' }}>On schedule</span>
      ),
    },
  ];

  return (
    <DataTable
      columns={columns}
      data={tasks}
      keyExtractor={(t) => t.task_id}
      emptyMessage="No maintenance tasks match the current filters."
      onRowClick={onRowClick}
      selectedRowId={selectedTaskId}
    />
  );
}