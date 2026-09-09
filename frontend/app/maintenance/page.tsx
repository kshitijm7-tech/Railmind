'use client';

import React, { useMemo } from 'react';
import { AppShell } from '../../components/layout/AppShell';
import { StateBadge } from '../../components/state/StateBadge';
import { LoadingState, EmptyState, ErrorState } from '../../components/feedback/FeedbackStates';
import { MetricCard } from '../../components/operational/MetricCard';
import { SectionBadge, DepartmentBadge, CriticalityBadge } from '../../components/railway/RailwayBadges';
import { Button } from '../../components/ui/Button';
import { MaintenanceKPIs } from '../../components/maintenance/MaintenanceKPIs';
import { MaintenanceFilters as MaintenanceFiltersComponent } from '../../components/maintenance/MaintenanceFilters';
import { MaintenanceTaskTable } from '../../components/maintenance/MaintenanceTaskTable';
import { MaintenanceTaskDetail } from '../../components/maintenance/MaintenanceTaskDetail';
import { MaintenancePlanningBridge } from '../../components/maintenance/MaintenancePlanningBridge';
import { useMaintenanceWorkspace } from '../../hooks/useMaintenanceWorkspace';
import type { MaintenanceFilters } from '../../hooks/useMaintenanceWorkspace';
import type { MaintenanceTask, Section, RailwayAsset, Incident } from '../../domain';

export default function MaintenancePage() {
  const {
    tasks,
    defects,
    network,
    filteredTasks,
    kpis,
    sections,
    assets,
    defectsBySection,
    getAssetById,
    getSectionById,
    getDefectsForTask,
    filters,
    selectedTaskId,
    setFilters,
    setSearchQuery,
    setSort,
    selectTask,
    refresh,
    isLoading,
  } = useMaintenanceWorkspace();

  const hasActiveFilters = useMemo(() => {
    return (
      filters.status !== 'ALL' ||
      filters.priority !== 'ALL' ||
      filters.type !== 'ALL' ||
      filters.sectionId !== '' ||
      filters.assetId !== '' ||
      filters.dueState !== 'ALL' ||
      filters.searchQuery !== ''
    );
  }, [filters]);

  const selectedTask = useMemo(() => {
    if (!selectedTaskId) return null;
    return filteredTasks.find((t) => t.task_id === selectedTaskId) ?? null;
  }, [selectedTaskId, filteredTasks]);

  const selectedTaskSection = useMemo(() => {
    if (!selectedTask) return undefined;
    return getSectionById(selectedTask.section_id);
  }, [selectedTask, getSectionById]);

  const selectedTaskAsset = useMemo(() => {
    if (!selectedTask || !selectedTask.asset_id) return undefined;
    return getAssetById(selectedTask.asset_id);
  }, [selectedTask, getAssetById]);

  const selectedTaskDefects = useMemo(() => {
    if (!selectedTask) return [];
    return getDefectsForTask(selectedTask);
  }, [selectedTask, getDefectsForTask]);

  const handleRowClick = (task: MaintenanceTask) => {
    if (selectedTaskId === task.task_id) {
      selectTask(null);
    } else {
      selectTask(task.task_id);
    }
  };

  const handlePlanTask = () => {
    // Navigate to planning page with context
    if (selectedTask) {
      window.location.href = `/planning?taskId=${selectedTask.task_id}`;
    } else {
      window.location.href = '/planning';
    }
  };

  // Render task list section
  const renderTaskList = () => {
    if (tasks.status === 'loading') {
      return <LoadingState message="Loading maintenance backlog..." />;
    }
    if (tasks.status === 'error') {
      return (
        <ErrorState
          title="Maintenance Backlog Unavailable"
          error={tasks.errorMessage ?? undefined}
          affectedScope="Maintenance task list"
          onRetry={refresh}
        />
      );
    }
    if (!tasks.data || tasks.data.length === 0) {
      return <EmptyState title="No maintenance tasks" description="No tasks are currently defined for this corridor." />;
    }

    return (
      <div className="maintenance-list-wrapper">
        <MaintenanceKPIs kpis={kpis} />
        <MaintenanceFiltersComponent
          filters={filters}
          sections={sections}
          assets={assets}
          onFiltersChange={setFilters}
          onSearchChange={setSearchQuery}
          onSortChange={setSort}
          onClear={() => setFilters({
            status: 'ALL',
            priority: 'ALL',
            type: 'ALL',
            sectionId: '',
            assetId: '',
            dueState: 'ALL',
            searchQuery: '',
            sort: 'priority-desc',
          })}
          hasActiveFilters={hasActiveFilters}
        />
        <MaintenanceTaskTable
          tasks={filteredTasks}
          onRowClick={handleRowClick}
          selectedTaskId={selectedTaskId}
        />
        <div className="list-footer">
          <span>{filteredTasks.length} of {tasks.data?.length ?? 0} tasks shown</span>
          {selectedTask && (
            <Button variant="secondary" size="sm" onClick={() => selectTask(null)}>
              Clear Selection
            </Button>
          )}
        </div>
      </div>
    );
  };

  // Render task detail panel
  const renderTaskDetail = () => {
    if (!selectedTask) {
      return (
        <div className="detail-placeholder" role="status">
          <EmptyState
            title="No task selected"
            description="Click a maintenance task to view its details, infrastructure context, defects, and planning readiness."
            actionLabel="Select a task"
            onAction={() => {}}
          />
        </div>
      );
    }

    if (tasks.status === 'error' && !tasks.data) {
      return (
        <ErrorState
          title="Unable to load task list"
          error={tasks.errorMessage ?? undefined}
          affectedScope="Task detail requires task list"
          onRetry={refresh}
        />
      );
    }

    return (
      <MaintenanceTaskDetail
        task={selectedTask}
        section={selectedTaskSection}
        asset={selectedTaskAsset}
        defects={selectedTaskDefects}
        onClose={() => selectTask(null)}
        onPlanTask={handlePlanTask}
      />
    );
  };

  // Determine which defect/incident data to show
  const activeIncidents = useMemo(() => {
    if (defects.status === 'success' && defects.data) {
      return defects.data.filter((d: Incident) => d.status !== 'Resolved');
    }
    return [];
  }, [defects]);

  return (
    <AppShell
      title="Maintenance Workspace"
      eyebrow="Possession & Defect Backlog"
      actions={
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <StateBadge stateType="PREDICTION" label="EXPLAINABLE PRIORITY SCORED" />
          <Button variant="outline" size="sm" onClick={refresh} disabled={isLoading} aria-label="Refresh maintenance data">
            ⟳ Refresh
          </Button>
        </div>
      }
    >
      {isLoading && (
        <LoadingState message="Loading corridor maintenance state..." />
      )}

      <div className="maintenance-workspace">
        {/* Network/Defect Alerts Bar */}
        {(activeIncidents.length > 0 || (network.status === 'success' && network.data)) && (
          <div className="maintenance-alerts-bar" aria-label="Active incidents and network alerts">
            {activeIncidents.length > 0 && (
              <div className="alert-chip critical">
                <span>⚠</span>
                <span>{activeIncidents.length} active incident(s) — {activeIncidents.filter((i: Incident) => i.severity === 'CRITICAL').length} critical</span>
              </div>
            )}
            {network.status === 'success' && network.data && (
              <div className="alert-chip info">
                <span>📍</span>
                <span>
                  {network.data.zone} · {network.data.corridor} · {network.data.sections.length} sections · {network.data.assets.length} assets
                </span>
              </div>
            )}
          </div>
        )}

        <div className="maintenance-main-grid">
          {/* Left: Task List */}
          <section className="maintenance-list-section" aria-labelledby="task-list-heading">
            <div className="section-header">
              <h2 id="task-list-heading" className="section-title">Maintenance Backlog</h2>
              <div className="section-meta">
                {tasks.status === 'success' && tasks.data && (
                  <span className="task-count">{tasks.data.length} tasks</span>
                )}
                <span className="data-source" data-source={tasks.source}>
                  {tasks.source === 'REAL' ? '● REAL' : tasks.source === 'MOCK' ? '● MOCK' : '● UNKNOWN'}
                </span>
              </div>
            </div>
            {renderTaskList()}
          </section>

          {/* Right: Task Detail + Planning Bridge */}
          <aside className="maintenance-detail-section" aria-labelledby="detail-heading">
            <div className="section-header">
              <h2 id="detail-heading" className="section-title">Task Detail</h2>
            </div>
            {renderTaskDetail()}

            {/* Planning Bridge at bottom of detail panel */}
            <MaintenancePlanningBridge
              onOpenPlanning={() => {
                if (selectedTask) {
                  window.location.href = `/planning?taskId=${selectedTask.task_id}`;
                } else {
                  window.location.href = '/planning';
                }
              }}
              disabled={false}
            />
          </aside>
        </div>

        {/* Defects/Incidents Panel */}
        {activeIncidents.length > 0 && (
          <section className="maintenance-defects-section" aria-labelledby="defects-heading">
            <div className="section-header">
              <h2 id="defects-heading" className="section-title">Active Defects & Incidents</h2>
              <span className="defect-count">{activeIncidents.length} active</span>
            </div>
            <div className="defects-grid">
              {activeIncidents.slice(0, 6).map((incident: Incident) => (
                <article key={incident.incident_id} className="defect-card">
                  <div className="defect-header">
                    <span className="defect-type">{incident.incident_type}</span>
                    <CriticalityBadge criticality={incident.severity} />
                  </div>
                  <h4 className="defect-title">{incident.title}</h4>
                  <p className="defect-description">{incident.description}</p>
                  <div className="defect-meta">
                    <span><SectionBadge sectionId={incident.section_id} /></span>
                    <span>Status: {incident.status}</span>
                    <span>Detected: {new Date(incident.detected_at).toLocaleString()}</span>
                  </div>
                </article>
              ))}
            </div>
          </section>
        )}
      </div>
    </AppShell>
  );
}