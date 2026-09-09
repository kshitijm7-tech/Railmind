'use client';

import React from 'react';
import { Button } from '../ui/Button';
import type { MaintenanceFilters, MaintenanceStatusFilter, PriorityFilter, TypeFilter, DueStateFilter, SortOption } from '../../hooks/useMaintenanceWorkspace';

interface MaintenanceFiltersProps {
  filters: MaintenanceFilters;
  sections: { section_id: string; name: string }[];
  assets: { asset_id: string; name: string }[];
  onFiltersChange: (partial: Partial<MaintenanceFilters>) => void;
  onSearchChange: (query: string) => void;
  onSortChange: (sort: SortOption) => void;
  onClear: () => void;
  hasActiveFilters: boolean;
}

const STATUS_OPTIONS: { value: MaintenanceFilters['status']; label: string }[] = [
  { value: 'ALL', label: 'All Status' },
  { value: 'Pending', label: 'Pending' },
  { value: 'Scheduled', label: 'Scheduled' },
  { value: 'In Progress', label: 'In Progress' },
  { value: 'Completed', label: 'Completed' },
  { value: 'Overdue', label: 'Overdue' },
  { value: 'Blocked', label: 'Blocked' },
  { value: 'Cancelled', label: 'Cancelled' },
];

const PRIORITY_OPTIONS: { value: PriorityFilter; label: string }[] = [
  { value: 'ALL', label: 'All Priority' },
  { value: 'CRITICAL', label: 'Critical' },
  { value: 'HIGH', label: 'High' },
  { value: 'MEDIUM', label: 'Medium' },
  { value: 'LOW', label: 'Low' },
];

const TYPE_OPTIONS: { value: TypeFilter; label: string }[] = [
  { value: 'ALL', label: 'All Types' },
  { value: 'Preventive', label: 'Preventive' },
  { value: 'Corrective', label: 'Corrective' },
  { value: 'Inspection', label: 'Inspection' },
  { value: 'Defect', label: 'Defect' },
];

const DUE_STATE_OPTIONS: { value: DueStateFilter; label: string }[] = [
  { value: 'ALL', label: 'All Due States' },
  { value: 'Overdue', label: 'Overdue' },
  { value: 'Due Today', label: 'Due Today' },
  { value: 'Due Soon', label: 'Due Soon (&le;3d)' },
  { value: 'Upcoming', label: 'Upcoming' },
  { value: 'No Deadline', label: 'No Deadline' },
];

const SORT_OPTIONS: { value: SortOption; label: string }[] = [
  { value: 'priority-desc', label: 'Priority &darr;' },
  { value: 'priority-asc', label: 'Priority &uarr;' },
  { value: 'due-date-asc', label: 'Due Date &uarr;' },
  { value: 'due-date-desc', label: 'Due Date &darr;' },
  { value: 'overdue-desc', label: 'Most Overdue' },
  { value: 'task-id-asc', label: 'Task ID A-Z' },
  { value: 'task-id-desc', label: 'Task ID Z-A' },
];

export function MaintenanceFilters({
  filters,
  sections,
  assets,
  onFiltersChange,
  onSearchChange,
  onSortChange,
  onClear,
  hasActiveFilters,
}: MaintenanceFiltersProps) {
  return (
    <div className="maintenance-filters" role="search" aria-label="Maintenance filters">
      <div className="filters-row">
        <div className="filter-group search-group">
          <label htmlFor="maintenance-search" className="visually-hidden">Search tasks</label>
          <input
            id="maintenance-search"
            type="search"
            placeholder="Search task ID, title, section, asset, type..."
            value={filters.searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="filter-input"
            aria-label="Search maintenance tasks"
          />
        </div>

        <div className="filter-group">
          <label htmlFor="status-filter" className="visually-hidden">Status</label>
          <select
            id="status-filter"
            value={filters.status}
            onChange={(e) => onFiltersChange({ status: e.target.value as any })}
            className="filter-select"
          >
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="priority-filter" className="visually-hidden">Priority</label>
          <select
            id="priority-filter"
            value={filters.priority}
            onChange={(e) => onFiltersChange({ priority: e.target.value as any })}
            className="filter-select"
          >
            {PRIORITY_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="type-filter" className="visually-hidden">Type</label>
          <select
            id="type-filter"
            value={filters.type}
            onChange={(e) => onFiltersChange({ type: e.target.value as any })}
            className="filter-select"
          >
            {TYPE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="section-filter" className="visually-hidden">Section</label>
          <select
            id="section-filter"
            value={filters.sectionId}
            onChange={(e) => onFiltersChange({ sectionId: e.target.value })}
            className="filter-select"
          >
            <option value="">All Sections</option>
            {sections.map((s) => (
              <option key={s.section_id} value={s.section_id}>
                {s.section_id} &mdash; {s.name}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="asset-filter" className="visually-hidden">Asset</label>
          <select
            id="asset-filter"
            value={filters.assetId}
            onChange={(e) => onFiltersChange({ assetId: e.target.value })}
            className="filter-select"
          >
            <option value="">All Assets</option>
            {assets.map((a) => (
              <option key={a.asset_id} value={a.asset_id}>
                {a.asset_id} &mdash; {a.name}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="due-state-filter" className="visually-hidden">Due State</label>
          <select
            id="due-state-filter"
            value={filters.dueState}
            onChange={(e) => onFiltersChange({ dueState: e.target.value as any })}
            className="filter-select"
          >
            {DUE_STATE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="sort-filter" className="visually-hidden">Sort</label>
          <select
            id="sort-filter"
            value={filters.sort}
            onChange={(e) => onSortChange(e.target.value as any)}
            className="filter-select"
          >
            {SORT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
      </div>

      {hasActiveFilters && (
        <div className="filters-active">
          <span className="filters-active-label">Active filters:</span>
          <div className="filters-active-chips">
            {filters.status !== 'ALL' && (
              <span className="filter-chip" onClick={() => onFiltersChange({ status: 'ALL' })}>
                Status: {filters.status} &times;
              </span>
            )}
            {filters.priority !== 'ALL' && (
              <span className="filter-chip" onClick={() => onFiltersChange({ priority: 'ALL' })}>
                Priority: {filters.priority} &times;
              </span>
            )}
            {filters.type !== 'ALL' && (
              <span className="filter-chip" onClick={() => onFiltersChange({ type: 'ALL' })}>
                Type: {filters.type} &times;
              </span>
            )}
            {filters.sectionId && (
              <span className="filter-chip" onClick={() => onFiltersChange({ sectionId: '' })}>
                Section: {filters.sectionId} &times;
              </span>
            )}
            {filters.assetId && (
              <span className="filter-chip" onClick={() => onFiltersChange({ assetId: '' })}>
                Asset: {filters.assetId} &times;
              </span>
            )}
            {filters.dueState !== 'ALL' && (
              <span className="filter-chip" onClick={() => onFiltersChange({ dueState: 'ALL' })}>
                Due: {filters.dueState} &times;
              </span>
            )}
            {filters.searchQuery && (
              <span className="filter-chip" onClick={() => onSearchChange('')}>
                Search query: {filters.searchQuery} &times;
              </span>
            )}
          </div>
          <Button variant="ghost" size="sm" onClick={onClear}>
            Clear All
          </Button>
        </div>
      )}
    </div>
  );
}