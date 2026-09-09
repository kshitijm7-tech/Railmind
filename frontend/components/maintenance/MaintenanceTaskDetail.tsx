'use client';

import React from 'react';
import { CriticalityBadge, DepartmentBadge, SectionBadge } from '../railway/RailwayBadges';
import { Button } from '../ui/Button';
import type { MaintenanceTask, Incident, Section, RailwayAsset } from '../../domain';
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
      return `Overdue by ${task.overdue_days} day(s)`;
    case 'Due Today':
      return 'Due today';
    case 'Due Soon':
      return task.latest_finish ? `Due in ${Math.ceil((new Date(task.latest_finish).getTime() - Date.now()) / (1000 * 60 * 60 * 24))} day(s)` : 'Due soon';
    case 'Upcoming':
      return task.latest_finish ? `Due ${new Date(task.latest_finish).toLocaleDateString()}` : 'Upcoming';
    case 'No Deadline':
    default:
      return 'No deadline specified';
  }
}

function getDueStateColor(task: MaintenanceTask): string {
  const state = getDueState(task);
  switch (state) {
    case 'Overdue': return 'var(--status-critical)';
    case 'Due Today': return 'var(--status-warning)';
    case 'Due Soon': return 'var(--status-attention)';
    case 'Upcoming': return 'var(--text-secondary)';
    case 'No Deadline':
    default: return 'var(--text-muted)';
  }
}

interface MaintenanceTaskDetailProps {
  task: MaintenanceTask;
  section?: Section;
  asset?: RailwayAsset;
  defects: Incident[];
  onClose: () => void;
  onPlanTask?: () => void;
}

export function MaintenanceTaskDetail({
  task,
  section,
  asset,
  defects,
  onClose,
  onPlanTask,
}: MaintenanceTaskDetailProps) {
  const overdue = task.overdue_days > 0;
  const dueState = getDueState(task);

  return (
    <div className="maintenance-task-detail" role="dialog" aria-labelledby="task-detail-title" aria-modal="true">
      <header className="detail-header">
        <div className="detail-title-group">
          <div className="detail-id-row">
            <span className="detail-task-id">{task.task_id}</span>
            <CriticalityBadge criticality={task.criticality} />
          </div>
          <h2 id="task-detail-title" className="detail-title">{task.title}</h2>
          <div className="detail-meta-row">
            <span className="detail-meta"><DepartmentBadge department={task.department} /></span>
            <span className="detail-meta"><SectionBadge sectionId={task.section_id} /></span>
            <span className="detail-meta" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>
              {task.task_type}
            </span>
          </div>
        </div>
        <Button variant="ghost" size="sm" onClick={onClose} aria-label="Close task detail">
          ✕ Close
        </Button>
      </header>

      <div className="detail-grid">
        {/* Overview */}
        <section className="detail-section" aria-labelledby="overview-heading">
          <h3 id="overview-heading" className="detail-section-title">Overview</h3>
          <dl className="detail-dl">
            <div className="detail-dt-dd">
              <dt>Task ID</dt>
              <dd><code>{task.task_id}</code></dd>
            </div>
            <div className="detail-dt-dd">
              <dt>Description</dt>
              <dd>{task.description || task.title}</dd>
            </div>
            <div className="detail-dt-dd">
              <dt>Type</dt>
              <dd>{task.task_type}</dd>
            </div>
            <div className="detail-dt-dd">
              <dt>Status</dt>
              <dd>
                <span style={{
                  textTransform: 'uppercase',
                  letterSpacing: '0.04em',
                  fontWeight: 600,
                  fontSize: '0.8rem',
                  color: task.status === 'Completed' ? 'var(--status-normal)' :
                         task.status === 'In Progress' ? 'var(--status-attention)' :
                         task.status === 'Overdue' || task.status === 'Blocked' ? 'var(--status-critical)' :
                         'var(--text-secondary)',
                }}>
                  {task.status}
                </span>
              </dd>
            </div>
            <div className="detail-dt-dd">
              <dt>Criticality</dt>
              <dd><CriticalityBadge criticality={task.criticality} /></dd>
            </div>
            <div className="detail-dt-dd">
              <dt>Priority Score</dt>
              <dd>
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: task.priority_score > 80 ? 'var(--status-critical)' : task.priority_score > 60 ? 'var(--status-warning)' : 'var(--text-accent)' }}>
                  {task.priority_score.toFixed(1)} / 100
                </span>
                {task.priority_breakdown && (
                  <details style={{ marginTop: '0.5rem' }}>
                    <summary style={{ cursor: 'pointer', color: 'var(--text-secondary)', fontSize: '0.75rem' }}>Breakdown</summary>
                    <ul style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                      <li>Criticality: {task.priority_breakdown.criticality_score}</li>
                      <li>Overdue: {task.priority_breakdown.overdue_factor}</li>
                      <li>Failure Risk: {task.priority_breakdown.failure_risk}</li>
                      <li>Safety: {task.priority_breakdown.safety_flag}</li>
                      <li>Downstream Impact: {task.priority_breakdown.downstream_impact}</li>
                    </ul>
                  </details>
                )}
              </dd>
            </div>
          </dl>
        </section>

        {/* Infrastructure Context */}
        <section className="detail-section" aria-labelledby="infrastructure-heading">
          <h3 id="infrastructure-heading" className="detail-section-title">Infrastructure Context</h3>
          <dl className="detail-dl">
            {asset && (
              <div className="detail-dt-dd">
                <dt>Asset</dt>
                <dd>
                  <strong>{asset.name}</strong> ({asset.asset_id})
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                    Type: {asset.asset_type} · Health: {asset.health_score}/100 · Status: {asset.status}
                  </div>
                </dd>
              </div>
            )}
            <div className="detail-dt-dd">
              <dt>Section</dt>
              <dd>
                {section ? (
                  <>
                    <strong>{section.name}</strong> ({section.section_id})
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                      {section.from_station_id} → {section.to_station_id} · {section.length_km} km · {section.track_count} track(s)
                    </div>
                  </>
                ) : (
                  <code>{task.section_id}</code>
                )}
              </dd>
            </div>
            {asset && (
              <div className="detail-dt-dd">
                <dt>Asset Health</dt>
                <dd>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{
                      width: '100px',
                      height: '6px',
                      background: 'var(--surface-border)',
                      borderRadius: '3px',
                      position: 'relative',
                      overflow: 'hidden',
                    }}>
                      <span style={{
                        display: 'block',
                        height: '100%',
                        width: `${asset.health_score}%`,
                        background: asset.health_score >= 80 ? 'var(--status-normal)' :
                                asset.health_score >= 50 ? 'var(--status-warning)' : 'var(--status-critical)',
                        borderRadius: '3px',
                      }} />
                    </span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>
                      {asset.health_score}/100
                    </span>
                  </div>
                </dd>
              </div>
            )}
            <div className="detail-dt-dd">
              <dt>Departments Involved</dt>
              <dd>
                <DepartmentBadge department={task.department} />
                {task.department !== 'Engineering' && task.department !== 'S&T' && (
                  <span style={{ marginLeft: '0.5rem', color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                    Primary department shown
                  </span>
                )}
              </dd>
            </div>
          </dl>
        </section>

        {/* Defect Context */}
        {defects.length > 0 && (
          <section className="detail-section" aria-labelledby="defects-heading">
            <h3 id="defects-heading" className="detail-section-title">Associated Defects ({defects.length})</h3>
            <div className="detail-defects">
              {defects.map((defect) => (
                <article key={defect.incident_id} className="defect-card">
                  <div className="defect-header">
                    <span className="defect-type">{defect.incident_type}</span>
                    <CriticalityBadge criticality={defect.severity} />
                  </div>
                  <h4 className="defect-title">{defect.title}</h4>
                  <p className="defect-description">{defect.description}</p>
                  <div className="defect-meta">
                    <span>Status: {defect.status}</span>
                    <span>Section: {defect.section_id}</span>
                    <span>Detected: {new Date(defect.detected_at).toLocaleString()}</span>
                  </div>
                </article>
              ))}
            </div>
          </section>
        )}

        {/* Work Scope */}
        <section className="detail-section" aria-labelledby="work-heading">
          <h3 id="work-heading" className="detail-section-title">Work Scope</h3>
          <dl className="detail-dl">
            <div className="detail-dt-dd">
              <dt>Type</dt>
              <dd>{task.task_type}</dd>
            </div>
            <div className="detail-dt-dd">
              <dt>Estimated Duration</dt>
              <dd>
                <strong>{task.expected_duration_min} minutes</strong>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                  P10: {task.duration_estimates.p10_min} min · P90: {task.duration_estimates.p90_min} min
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.125rem' }}>
                  Overrun probability: {(task.duration_estimates.overrun_probability * 100).toFixed(0)}% · Confidence: {(task.duration_estimates.confidence * 100).toFixed(0)}%
                </div>
              </dd>
            </div>
            <div className="detail-dt-dd">
              <dt>Crew Required</dt>
              <dd>{task.crew_size_required} × {task.crew_qualification}</dd>
            </div>
            <div className="detail-dt-dd">
              <dt>Power Block Required</dt>
              <dd>{task.requires_power_block ? 'Yes' : 'No'}</dd>
            </div>
            <div className="detail-dt-dd">
              <dt>Traffic Block Required</dt>
              <dd>{task.requires_traffic_block ? 'Yes' : 'No'}</dd>
            </div>
          </dl>
        </section>

        {/* Timing */}
        <section className="detail-section" aria-labelledby="timing-heading">
          <h3 id="timing-heading" className="detail-section-title">Timing & Deadlines</h3>
          <dl className="detail-dl">
            <div className="detail-dt-dd">
              <dt>Earliest Start</dt>
              <dd>{task.earliest_start ? new Date(task.earliest_start).toLocaleString() : 'Not specified'}</dd>
            </div>
            <div className="detail-dt-dd">
              <dt>Latest Finish</dt>
              <dd>
                {task.latest_finish ? new Date(task.latest_finish).toLocaleString() : 'Not specified'}
                {task.latest_finish && (
                  <span style={{ marginLeft: '0.5rem', color: getDueStateColor(task), fontWeight: 600, fontSize: '0.75rem' }}>
                    ({getDueStateLabel(task)})
                  </span>
                )}
              </dd>
            </div>
            <div className="detail-dt-dd">
              <dt>Overdue</dt>
              <dd>
                {overdue ? (
                  <span style={{ color: 'var(--status-critical)', fontWeight: 700 }}>
                    {task.overdue_days} day(s) overdue
                  </span>
                ) : (
                  <span style={{ color: 'var(--text-muted)' }}>Not overdue</span>
                )}
              </dd>
            </div>
            <div className="detail-dt-dd">
              <dt>Dependencies</dt>
              <dd>
                {task.dependency_task_ids.length > 0 ? (
                  <ul style={{ fontSize: '0.8rem' }}>
                    {task.dependency_task_ids.map((dep) => (
                      <li key={dep}><code>{dep}</code></li>
                    ))}
                  </ul>
                ) : (
                  <span style={{ color: 'var(--text-muted)' }}>None</span>
                )}
              </dd>
            </div>
          </dl>
        </section>

        {/* Possession / Planning Bridge */}
        <section className="detail-section" aria-labelledby="possession-heading">
          <h3 id="possession-heading" className="detail-section-title">Possession & Planning</h3>
          <dl className="detail-dl">
            <div className="detail-dt-dd">
              <dt>Power Block</dt>
              <dd>{task.requires_power_block ? 'Required' : 'Not required'}</dd>
            </div>
            <div className="detail-dt-dd">
              <dt>Traffic Block</dt>
              <dd>{task.requires_traffic_block ? 'Required' : 'Not required'}</dd>
            </div>
            <div className="detail-dt-dd">
              <dt>Possession Planning</dt>
              <dd>
                <div style={{ color: 'var(--status-attention)' }}>
                  <strong>Not yet calculated</strong>
                </div>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                  Possession windows, candidate blocks, and operational impact require
                  the Constraint Engine and Optimization Engine (E01/E03 — not yet implemented).
                </p>
              </dd>
            </div>
            <div className="detail-dt-dd">
              <dt>Train Impact</dt>
              <dd>
                <div style={{ color: 'var(--status-attention)' }}>
                  <strong>Not calculated</strong>
                </div>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                  Train impact analysis requires the Optimization Engine and Simulation Engine (E03/E06 — not yet implemented).
                </p>
              </dd>
            </div>
            <div className="detail-dt-dd">
              <dt>Crew & Resource Optimization</dt>
              <dd>
                <div style={{ color: 'var(--status-attention)' }}>
                  <strong>Not optimized</strong>
                </div>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                  Crew allocation and resource optimization require the Optimization Engine (E03 — not yet implemented).
                </p>
              </dd>
            </div>
          </dl>

          {onPlanTask && (
            <div className="detail-action-row">
              <Button variant="primary" size="sm" onClick={onPlanTask}>
                Plan Task in Block Planning →
              </Button>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                Forward to CP-SAT solver workspace for possession allocation
              </span>
            </div>
          )}
        </section>

        {/* Provenance */}
        <section className="detail-section" aria-labelledby="provenance-heading">
          <h3 id="provenance-heading" className="detail-section-title">Data Provenance</h3>
          <dl className="detail-dl">
            <div className="detail-dt-dd">
              <dt>Source</dt>
              <dd>
                <span className={`provenance-badge provenance-${(task as any)._source?.toLowerCase() ?? 'unknown'}`}>
                  {(task as any)._source ?? 'UNKNOWN'}
                </span>
              </dd>
            </div>
            {(task as any)._provenance && (
              <div className="detail-dt-dd">
                <dt>Provenance</dt>
                <dd>
                  <code style={{ fontSize: '0.7rem' }}>
                    State: {(task as any)._provenance.state ?? '—'} ·
                    Source: {(task as any)._provenance.source ?? '—'} ·
                    Generated: {(task as any)._provenance.generatedAt ?? '—'}
                  </code>
                </dd>
              </div>
            )}
          </dl>
        </section>
      </div>

      <footer className="detail-footer">
        <Button variant="secondary" size="sm" onClick={onClose}>
          Close
        </Button>
      </footer>
    </div>
  );
}