import { describe, it, expect, vi } from 'vitest';
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MaintenanceKPIs } from '../components/maintenance/MaintenanceKPIs';
import { MaintenanceFilters } from '../components/maintenance/MaintenanceFilters';
import { MaintenanceTaskTable } from '../components/maintenance/MaintenanceTaskTable';
import { MaintenancePlanningBridge } from '../components/maintenance/MaintenancePlanningBridge';
import type { MaintenanceFilters as Filters } from '../hooks/useMaintenanceWorkspace';
import type { MaintenanceTask } from '../domain';

function makeTask(overrides: Partial<MaintenanceTask> = {}): MaintenanceTask {
  return {
    task_id: 'TSK-101',
    title: 'Deep Screening & Tamping over SEC-04 Switch',
    section_id: 'SEC-04',
    asset_id: 'AST-TRK-01',
    department: 'Engineering',
    task_type: 'Defect',
    expected_duration_min: 180,
    duration_estimates: { expected_min: 180, p10_min: 150, p90_min: 240, overrun_probability: 0.28, confidence: 0.91 },
    crew_size_required: 8,
    crew_qualification: 'Engineering',
    criticality: 'CRITICAL',
    overdue_days: 3,
    dependency_task_ids: [],
    earliest_start: '2026-09-08T02:00:00Z',
    latest_finish: '2026-09-08T08:00:00Z',
    priority_score: 94.5,
    status: 'Pending',
    ...overrides,
  };
}

const BASE_FILTERS: Filters = {
  status: 'ALL',
  priority: 'ALL',
  type: 'ALL',
  sectionId: '',
  assetId: '',
  dueState: 'ALL',
  searchQuery: '',
  sort: 'priority-desc',
};

describe('MaintenanceKPIs', () => {
  it('renders derived counts without fabricated metrics', () => {
    render(
      <MaintenanceKPIs
        kpis={{ critical: 2, high: 3, overdue: 1, dueSoon: 2, open: 5, inProgress: 1, completed: 4, total: 10 }}
      />,
    );
    expect(screen.getByText('Critical')).toBeDefined();
    expect(screen.getByText('Overdue')).toBeDefined();
    expect(screen.getByText('Due Soon')).toBeDefined();
    expect(screen.getByText('In Progress')).toBeDefined();
  });
});

describe('MaintenanceFilters', () => {
  it('renders search, selects, and sort controls', () => {
    render(
      <MaintenanceFilters
        filters={BASE_FILTERS}
        sections={[{ section_id: 'SEC-04', name: 'Chhatarpur Single' }]}
        assets={[{ asset_id: 'AST-TRK-01', name: 'Turnout 104A' }]}
        onFiltersChange={() => {}}
        onSearchChange={() => {}}
        onSortChange={() => {}}
        onClear={() => {}}
        hasActiveFilters={false}
      />,
    );
    expect(screen.getByLabelText('Search maintenance tasks')).toBeDefined();
    expect(screen.getByLabelText('Status')).toBeDefined();
    expect(screen.getByLabelText('Sort')).toBeDefined();
  });

  it('emits search changes and shows active filter chips', () => {
    const onSearch = vi.fn();
    render(
      <MaintenanceFilters
        filters={{ ...BASE_FILTERS, searchQuery: 'SEC-04', priority: 'CRITICAL' }}
        sections={[]}
        assets={[]}
        onFiltersChange={() => {}}
        onSearchChange={onSearch}
        onSortChange={() => {}}
        onClear={() => {}}
        hasActiveFilters
      />,
    );
    fireEvent.change(screen.getByLabelText('Search maintenance tasks'), { target: { value: 'SEC-06' } });
    expect(onSearch).toHaveBeenCalledWith('SEC-06');
    expect(screen.getByText('Active filters:')).toBeDefined();
  });
});

describe('MaintenanceTaskTable', () => {
  const tasks = [
    makeTask(),
    makeTask({ task_id: 'TSK-102', title: 'Signal interlocking test', criticality: 'HIGH', priority_score: 82, overdue_days: 0, status: 'Scheduled', task_type: 'Preventive' }),
  ];

  it('renders task rows with priority, status, and due state', () => {
    render(<MaintenanceTaskTable tasks={tasks} selectedTaskId={null} />);
    expect(screen.getByText('TSK-101')).toBeDefined();
    expect(screen.getByText('TSK-102')).toBeDefined();
    expect(screen.getByText('CRITICAL')).toBeDefined();
  });

  it('renders an operational empty state when filters exclude everything', () => {
    render(<MaintenanceTaskTable tasks={[]} selectedTaskId={null} />);
    expect(screen.getByText('No maintenance tasks match the current filters.')).toBeDefined();
  });

  it('notifies row selection for the detail workspace', () => {
    const onRowClick = vi.fn();
    render(<MaintenanceTaskTable tasks={tasks} onRowClick={onRowClick} selectedTaskId={null} />);
    fireEvent.click(screen.getByText('TSK-101'));
    expect(onRowClick).toHaveBeenCalledTimes(1);
    expect(onRowClick.mock.calls[0]?.[0]?.task_id).toBe('TSK-101');
  });
});

describe('MaintenancePlanningBridge', () => {
  it('is honest about missing possession/optimization capabilities', () => {
    render(<MaintenancePlanningBridge disabled />);
    expect(screen.getByText('Planning Bridge')).toBeDefined();
    expect(screen.getAllByText(/not yet implemented/i).length).toBeGreaterThan(0);
  });
});
