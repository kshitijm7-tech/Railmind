'use client';

/**
 * F03 — Maintenance Workspace data aggregation hook.
 *
 * Flow:
 *   MaintenanceWorkspace
 *     -> useMaintenanceWorkspace
 *     -> useApiQuery per section (tasks, defects, network)
 *     -> services.maintenance / services.network
 *     -> API / mock
 *     -> SectionSnapshot<T> with independent states
 *
 * Provides:
 * - Tasks with derived KPIs
 * - Defects/incidents
 * - Network context (assets, sections)
 * - Filtering, sorting, search state
 * - Task selection for detail view
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { services } from '../services';
import { useApiQuery, type SectionSnapshot, type ApiQueryState } from './useApiQuery';
import type {
  MaintenanceTask,
  Incident,
  RailwayNetwork,
  Section,
  RailwayAsset,
} from '../domain';
import { RailmindApiError, toUserMessage } from '../services/api/client/errors';

export type MaintenanceStatusFilter =
  | 'ALL'
  | 'Pending'
  | 'Scheduled'
  | 'In Progress'
  | 'Completed'
  | 'Overdue'
  | 'Blocked'
  | 'Cancelled';

export type PriorityFilter = 'ALL' | 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';

export type TypeFilter = 'ALL' | 'Preventive' | 'Corrective' | 'Inspection' | 'Defect';

export type DueStateFilter = 'ALL' | 'Overdue' | 'Due Today' | 'Due Soon' | 'Upcoming' | 'No Deadline';

export type SortOption =
  | 'priority-desc'
  | 'priority-asc'
  | 'due-date-asc'
  | 'due-date-desc'
  | 'task-id-asc'
  | 'task-id-desc'
  | 'criticality-desc'
  | 'overdue-desc';

export interface MaintenanceFilters {
  status: MaintenanceStatusFilter;
  priority: PriorityFilter;
  type: TypeFilter;
  sectionId: string;
  assetId: string;
  dueState: DueStateFilter;
  searchQuery: string;
  sort: SortOption;
}

export interface MaintenanceWorkspaceState {
  tasks: SectionSnapshot<MaintenanceTask[]>;
  defects: SectionSnapshot<Incident[]>;
  network: SectionSnapshot<RailwayNetwork>;
  filters: MaintenanceFilters;
  selectedTaskId: string | null;
  setFilters: (filters: Partial<MaintenanceFilters>) => void;
  setSearchQuery: (query: string) => void;
  setSort: (sort: SortOption) => void;
  selectTask: (taskId: string | null) => void;
  refresh: () => void;
  isLoading: boolean;
  // Derived
  filteredTasks: MaintenanceTask[];
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
  sections: Section[];
  assets: RailwayAsset[];
  defectsBySection: Record<string, Incident[]>;
  getAssetById: (assetId: string) => RailwayAsset | undefined;
  getSectionById: (sectionId: string) => Section | undefined;
  getDefectsForTask: (task: MaintenanceTask) => Incident[];
}

const DEFAULT_FILTERS: MaintenanceFilters = {
  status: 'ALL',
  priority: 'ALL',
  type: 'ALL',
  sectionId: '',
  assetId: '',
  dueState: 'ALL',
  searchQuery: '',
  sort: 'priority-desc',
};

export function computeDueState(task: MaintenanceTask): DueStateFilter {
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

export function matchesMaintenanceFilter(task: MaintenanceTask, filters: MaintenanceFilters): boolean {
  if (filters.status !== 'ALL' && task.status !== filters.status) return false;
  if (filters.priority !== 'ALL' && task.criticality !== filters.priority) return false;
  if (filters.type !== 'ALL' && task.task_type !== filters.type) return false;
  if (filters.sectionId && task.section_id !== filters.sectionId) return false;
  if (filters.assetId && task.asset_id !== filters.assetId) return false;
  if (filters.dueState !== 'ALL' && computeDueState(task) !== filters.dueState) return false;
  if (filters.searchQuery) {
    const q = filters.searchQuery.toLowerCase();
    const searchable = [
      task.task_id,
      task.title,
      task.section_id,
      task.asset_id ?? '',
      task.department,
      task.task_type,
    ].join(' ').toLowerCase();
    if (!searchable.includes(q)) return false;
  }
  return true;
}

export function sortMaintenanceTasks(tasks: MaintenanceTask[], sort: SortOption): MaintenanceTask[] {
  const sorted = [...tasks];
  switch (sort) {
    case 'priority-desc':
      return sorted.sort((a, b) => {
        const priorityOrder: Record<string, number> = { CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1 };
        const diff = priorityOrder[b.criticality] - priorityOrder[a.criticality];
        if (diff !== 0) return diff;
        return b.priority_score - a.priority_score;
      });
    case 'priority-asc':
      return sorted.sort((a, b) => {
        const priorityOrder: Record<string, number> = { CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1 };
        const diff = priorityOrder[a.criticality] - priorityOrder[b.criticality];
        if (diff !== 0) return diff;
        return a.priority_score - b.priority_score;
      });
    case 'due-date-asc':
      return sorted.sort((a, b) => {
        if (!a.latest_finish && !b.latest_finish) return 0;
        if (!a.latest_finish) return 1;
        if (!b.latest_finish) return -1;
        return new Date(a.latest_finish!).getTime() - new Date(b.latest_finish!).getTime();
      });
    case 'due-date-desc':
      return sorted.sort((a, b) => {
        if (!a.latest_finish && !b.latest_finish) return 0;
        if (!a.latest_finish) return 1;
        if (!b.latest_finish) return -1;
        return new Date(b.latest_finish!).getTime() - new Date(a.latest_finish!).getTime();
      });
    case 'task-id-asc':
      return sorted.sort((a, b) => a.task_id.localeCompare(b.task_id));
    case 'task-id-desc':
      return sorted.sort((a, b) => b.task_id.localeCompare(a.task_id));
    case 'criticality-desc':
      return sorted.sort((a, b) => {
        const order: Record<string, number> = { CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1 };
        return order[b.criticality] - order[a.criticality];
      });
    case 'overdue-desc':
      return sorted.sort((a, b) => b.overdue_days - a.overdue_days);
    default:
      return sorted;
  }
}

export function useMaintenanceWorkspace(): MaintenanceWorkspaceState {
  const [filters, setFiltersState] = useState<MaintenanceFilters>(DEFAULT_FILTERS);
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);

  // Fetch tasks
  const tasksQuery = useApiQuery<MaintenanceTask[]>(
    useCallback((signal) => services.maintenance.getTasks({}), []),
    { immediate: true, depsKey: 'tasks' }
  );

  // Fetch defects/incidents
  const defectsQuery = useApiQuery<Incident[]>(
    useCallback((signal) => services.maintenance.getDefects({}), []),
    { immediate: true, depsKey: 'defects' }
  );

  // Fetch network for asset/section context
  const networkQuery = useApiQuery<RailwayNetwork>(
    useCallback((signal) => services.network.getNetwork(), []),
    { immediate: true, depsKey: 'network' }
  );

  const isLoading = tasksQuery.status === 'loading' || defectsQuery.status === 'loading' || networkQuery.status === 'loading';

  // Derived filtered & sorted tasks
  const filteredTasks = useMemo(() => {
    if (!tasksQuery.data) return [];
    let result = tasksQuery.data.filter((t) => matchesMaintenanceFilter(t, filters));
    return sortMaintenanceTasks(result, filters.sort);
  }, [tasksQuery.data, filters]);

  // KPI calculations
  const kpis = useMemo(() => {
    const allTasks = tasksQuery.data ?? [];
    const critical = allTasks.filter((t) => t.criticality === 'CRITICAL' && t.status !== 'Completed' && t.status !== 'Cancelled').length;
    const high = allTasks.filter((t) => t.criticality === 'HIGH' && t.status !== 'Completed' && t.status !== 'Cancelled').length;
    const overdue = allTasks.filter((t) => t.overdue_days > 0 && t.status !== 'Completed' && t.status !== 'Cancelled').length;
    const dueSoon = allTasks.filter((t) => {
      const state = t.overdue_days > 0 ? 'Overdue' : !t.latest_finish ? 'No Deadline' : (() => {
        const finish = new Date(t.latest_finish!);
        const now = new Date();
        const diff = Math.ceil((finish.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
        if (diff < 0) return 'Overdue';
        if (diff === 0) return 'Due Today';
        if (diff <= 3) return 'Due Soon';
        return 'Upcoming';
      })();
      return state === 'Due Today' || state === 'Due Soon';
    }).length;
    const open = allTasks.filter((t) => t.status === 'Pending' || t.status === 'Scheduled').length;
    const inProgress = allTasks.filter((t) => t.status === 'In Progress').length;
    const completed = allTasks.filter((t) => t.status === 'Completed').length;
    return { critical, high, overdue, dueSoon, open, inProgress, completed, total: allTasks.length };
  }, [tasksQuery.data]);

  // Sections for filter dropdown
  const sections = useMemo(() => {
    if (!networkQuery.data) return [];
    return networkQuery.data.sections;
  }, [networkQuery.data]);

  // Assets for filter dropdown
  const assets = useMemo(() => {
    if (!networkQuery.data) return [];
    return networkQuery.data.assets;
  }, [networkQuery.data]);

  // Defects grouped by section
  const defectsBySection = useMemo(() => {
    const map: Record<string, Incident[]> = {};
    for (const defect of defectsQuery.data ?? []) {
      if (!map[defect.section_id]) map[defect.section_id] = [];
      map[defect.section_id].push(defect);
    }
    return map;
  }, [defectsQuery.data]);

  // Get asset by ID
  const getAssetById = useCallback((assetId: string): RailwayAsset | undefined => {
    return assets.find((a) => a.asset_id === assetId);
  }, [assets]);

  // Get section by ID
  const getSectionById = useCallback((sectionId: string): Section | undefined => {
    return sections.find((s) => s.section_id === sectionId);
  }, [sections]);

  // Get defects for a task
  const getDefectsForTask = useCallback((task: MaintenanceTask): Incident[] => {
    const sectionDefects = defectsBySection[task.section_id] ?? [];
    return sectionDefects.filter((d) => {
      // Match by asset if available, otherwise by section
      if (task.asset_id) return d.description?.toLowerCase().includes(task.asset_id.toLowerCase()) || false;
      return true;
    });
  }, [defectsBySection]);

  // Refresh all queries
  const refresh = useCallback(() => {
    tasksQuery.reload();
    defectsQuery.reload();
    networkQuery.reload();
  }, [tasksQuery, defectsQuery, networkQuery]);

  const setFilters = useCallback((partial: Partial<MaintenanceFilters>) => {
    setFiltersState((prev) => ({ ...prev, ...partial }));
  }, []);

  const setSearchQuery = useCallback((query: string) => {
    setFiltersState((prev) => ({ ...prev, searchQuery: query }));
  }, []);

  const setSort = useCallback((sort: SortOption) => {
    setFiltersState((prev) => ({ ...prev, sort }));
  }, []);

  const selectTask = useCallback((taskId: string | null) => {
    setSelectedTaskId(taskId);
  }, []);

  return {
    tasks: tasksQuery,
    defects: defectsQuery,
    network: networkQuery,
    filters,
    selectedTaskId,
    setFilters,
    setSearchQuery,
    setSort,
    selectTask,
    refresh,
    isLoading,
    // Derived
    filteredTasks,
    kpis,
    sections,
    assets,
    defectsBySection,
    getAssetById,
    getSectionById,
    getDefectsForTask,
  };
}