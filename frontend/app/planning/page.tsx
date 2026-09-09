'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { AppShell } from '../../components/layout/AppShell';
import { DataTable, ColumnDef } from '../../components/operational/DataTable';
import { SectionCard } from '../../components/command-center/SectionCard';
import { Button } from '../../components/ui/Button';
import { services } from '../../services';
import type { Plan as DomainPlan } from '../../domain';
import { EmptyState } from '../../components/feedback/FeedbackStates';

// Window columns - array since DataTable expects ColumnDef<T>[]
const windowColumns: ColumnDef<any>[] = [
  { header: 'Window ID', cell: (w: any) => <strong style={{ fontFamily: 'var(--font-mono)' }}>{w.window_id}</strong> },
  { header: 'Section', cell: (w: any) => w.section_id },
  { header: 'Start', cell: (w: any) => w.earliest_start },
  { header: 'End', cell: (w: any) => w.latest_end },
  { header: 'Duration', cell: (w: any) => `${w.max_duration_min} min` },
  { header: 'Feasibility', cell: (w: any) => {
    const feasibilityMap: Record<string, string> = {
      'FEASIBLE': 'FEASIBLE',
      'INFEASIBLE': 'INFEASIBLE',
      'PENDING': 'PENDING',
      'UNKNOWN': 'UNKNOWN',
    };
    return feasibilityMap[w.feasibility] || 'UNKNOWN';
  } },
];

// Plan columns - array since DataTable expects ColumnDef<T>[]
const planColumns: ColumnDef<DomainPlan>[] = [
  { header: 'Plan ID', cell: (p: DomainPlan) => <strong style={{ fontFamily: 'var(--font-mono)' }}>{p.plan_id}</strong> },
  { header: 'Strategy', cell: (p: DomainPlan) => p.strategy },
  { header: 'Status', cell: (p: DomainPlan) => p.status },
  { header: 'Predicted Delay', cell: (p: DomainPlan) => `${p.metrics.total_delay_minutes} min` },
  { header: 'Tasks Done', cell: (p: DomainPlan) => `${p.metrics.maintenance_tasks_completed} tasks` },
  { header: 'Overrun Risk (P90)', cell: (p: DomainPlan) => `${(p.metrics.overall_overrun_risk * 100).toFixed(0)}%` },
  { header: 'Solver Time', cell: (p: DomainPlan) => `${p.solver_runtime_ms} ms` },
  { header: 'Feasible', cell: (p: DomainPlan) => {
    const statusMap: Record<string, string> = {
      'FEASIBLE': 'FEASIBLE',
      'INFEASIBLE': 'INFEASIBLE',
    };
    return statusMap[p.status] || 'UNKNOWN';
  } },
];

function PlanningWorkspace() {
  // Use any[] for plans since domain type may not match all UI needs
  const [plans, setPlans] = useState<any[]>([]);
  const [windows, setWindows] = useState<any[]>([]);
  const [selectedPlan, setSelectedPlan] = useState<any | null>(null);
  const [generateJob, setGenerateJob] = useState<{ jobId?: string; status?: string } | null>(null);
  const [constraintViolations, setConstraintViolations] = useState<any[]>([]);

  // Load planning data
  useEffect(() => {
    services.planning.getPlans().then((pList: any[]) => setPlans(pList));
    services.planning.getCandidateWindows().then((wList: any[]) => setWindows(wList));
  }, []);

  // Plan selection handler
  const handlePlanSelect = useCallback((plan: any) => {
    setSelectedPlan(plan);
    // Use mock constraint data based on plan status
    const mockViolations: any[] = [];
    if (plan.status === 'INFEASIBLE' || plan.status === 'Rejected') {
      mockViolations.push({
        id: 'CONST-001',
        name: 'Track Occupancy Conflict',
        type: 'HARD',
        status: 'VIOLATED',
        description: 'Proposed block conflicts with existing operational occupancy on Section SEC-03',
        affectedResource: 'Section SEC-03',
      });
      mockViolations.push({
        id: 'CONST-002',
        name: 'Mandatory Safety Restriction',
        type: 'HARD',
        status: 'VIOLATED',
        description: 'Safety restriction prohibits maintenance during peak passenger hours',
        affectedResource: 'Peak hours 07:00-09:00',
      });
    }
    setConstraintViolations(mockViolations);
  }, []);

  // Generate plan handler
  const handleGeneratePlan = useCallback(async (request: any) => {
    setGenerateJob(null);
    try {
      const job = await services.planning.generatePlan(request);
      setGenerateJob({ jobId: job.jobId, status: job.status });
    } catch (error: any) {
      console.error('Plan generation failed:', error);
      setGenerateJob({ jobId: 'JOB-ERR', status: 'FAILED' });
    }
  }, []);

  // Compare plans handler
  const handleComparePlans = useCallback(async (planIds: string[]) => {
    try {
      await services.planning.comparePlans({ planIds: planIds as any });
    } catch (error: any) {
      console.error('Plan comparison failed:', error);
    }
  }, []);

  // Plan detail close
  const handlePlanClose = useCallback(() => {
    setSelectedPlan(null);
    setConstraintViolations([]);
  }, []);

  return (
    <AppShell
      title="Block Planning & Possession Workspace"
      eyebrow="Constraint-aware block planning — system generated candidates pending human review"
      actions={
        <>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => handleComparePlans(plans.slice(0, 3).map((p: any) => p.plan_id))}
            disabled={plans.length < 2}
            style={{ marginRight: '0.5rem' }}
          >
            Compare Plans
          </Button>
          {generateJob && (
            <Button
              variant="secondary"
              size="sm"
              onClick={() => {/* navigate to decision workspace */}
              }
              disabled={generateJob.status !== 'COMPLETED'}
            >
              {generateJob.status === 'COMPLETED' ? 'View Result' : 'Pending Review'}
            </Button>
          )}
          <Button
            variant="secondary"
            size="sm"
            onClick={() => {/* open maintenance workspace for task selection */}
            }
            style={{ marginLeft: '0.5rem' }}
          >
            ← Back to Maintenance
          </Button>
        </>
      }
    >
      <div style={{ marginBottom: '1.5rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
        Joint planning of maintenance possessions and train paths under hard safety and resource constraints.
      </div>

      {/* Planning Context Section */}
      <SectionCard
        eyebrow="F04 Block Planning"
        title="Planning Context"
        status="success"
      >
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          {/* Task Context */}
          <div>
            <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem' }}>Maintenance Task</h4>
            {plans.length > 0 ? (
              <>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                  <strong>Task:</strong> {plans[0]?.task_id || '—'}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                  <strong>Title:</strong> {plans[0]?.title || '—'}
                </div>
              </>
            ) : (
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                No task selected — select a maintenance task from the Maintenance Workspace to planning context
              </div>
            )}
            <div style={{ marginTop: '0.5rem' }}>
              <span style={{
                marginRight: '0.5rem',
                padding: '2px 6px',
                background: 'var(--surface-panel)',
                border: '1px solid var(--surface-border)',
                borderRadius: '3px',
                fontSize: '0.65rem',
                color: 'var(--text-primary)',
              }}>
                Preventive / HIGH priority
              </span>
              <span style={{
                padding: '2px 6px',
                background: 'var(--surface-panel)',
                border: '1px solid var(--surface-border)',
                borderRadius: '3px',
                fontSize: '0.65rem',
                color: 'var(--text-primary)',
              }}>
                Section: SEC-03
              </span>
            </div>
          </div>

          {/* Block Requirements */}
          <div>
            <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem' }}>Block / Possession Requirements</h4>
            <div style={{ fontSize: '0.75rem', marginBottom: '0.25rem' }}>
              <span style={{
                marginRight: '0.25rem',
                padding: '2px 6px',
                background: 'var(--status-approved)',
                border: '1px solid var(--surface-border)',
                borderRadius: '3px',
                fontSize: '0.65rem',
                color: 'var(--status-approved-fg)',
              }}>
                Power Block: Required
              </span>
              <span style={{
                marginRight: '0.25rem',
                padding: '2px 6px',
                background: 'var(--surface-panel)',
                border: '1px solid var(--surface-border)',
                borderRadius: '3px',
                fontSize: '0.65rem',
                color: 'var(--text-primary)',
              }}>
                Traffic Block: Not required
              </span>
            </div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
              Possession Window: 2026-01-15 — 2026-01-22
            </div>
          </div>
        </div>
      </SectionCard>

      {/* Candidate Windows Section */}
      <SectionCard
        eyebrow="Candidate Windows"
        title="Candidate Windows"
        status="success"
      >
        {windows.length === 0 ? (
          <EmptyState
            title="No candidate windows currently available"
            description={
              'Candidate window generation is not currently available on the backend. This endpoint is stubbed.'
            }
            actionLabel='Switch to MOCK mode'
          />
        ) : (
          <DataTable
            columns={windowColumns}
            data={windows}
            keyExtractor={(w: any) => w.window_id}
          />
        )}
      </SectionCard>

      {/* Constraints Section */}
      <SectionCard
        eyebrow="Constraints"
        title="Constraints"
        status="success"
      >
        {selectedPlan ? (
          <div style={{ fontSize: '0.75rem' }}>
            {constraintViolations.length === 0 ? (
              <div style={{ color: 'var(--text-secondary)' }}>
                All hard constraints are satisfied for this plan.
              </div>
            ) : (
              <div>{constraintViolations.map((cv: any, i: number) => (
                <div key={cv.id} style={{ padding: '0.5rem 0', borderBottom: '1px solid var(--surface-border)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                    <span style={{
                      padding: '2px 6px',
                      background: cv.type === 'HARD' ? 'var(--status-critical)' : 'var(--surface-panel)',
                      border: '1px solid var(--surface-border)',
                      borderRadius: '3px',
                      fontSize: '0.65rem',
                      fontWeight: 600,
                      color: cv.type === 'HARD' ? 'var(--status-critical-fg)' : 'var(--text-primary)',
                    }}>
                      {cv.type}: {cv.name}
                    </span>
                    <span style={{
                      padding: '2px 6px',
                      background: cv.status === 'VIOLATED' ? 'var(--status-critical)' : 'var(--surface-panel)',
                      border: '1px solid var(--surface-border)',
                      borderRadius: '3px',
                      fontSize: '0.65rem',
                      color: cv.status === 'VIOLATED' ? 'var(--status-critical-fg)' : 'var(--text-primary)',
                    }}>
                      {cv.status}
                    </span>
                  </div>
                  <p style={{ fontSize: '0.65rem', color: 'var(--text-secondary)', margin: '0.25rem 0' }}>
                    {cv.description}
                  </p>
                  {cv.affectedResource && (
                    <p style={{ fontSize: '0.65rem', color: 'var(--text-secondary)', margin: '0' }}>
                      Affected: {cv.affectedResource}
                    </p>
                  )}
                </div>
              ))}</div>
            )}
          </div>
        ) : (
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
            Select a plan to view constraint status.
          </div>
        )}
      </SectionCard>

      {/* Candidate Plans Section */}
      <SectionCard
        eyebrow="Candidate Plans"
        title="Candidate Plans"
        status="success"
      >
        {plans.length === 0 ? (
          <EmptyState
            title="No candidate plans available"
            description={
              'No plans are currently available. Plan generation has not been triggered or no plans match the current context.'
            }
            actionLabel='Generate Plan'
          />
        ) : (
          <DataTable
            columns={planColumns}
            data={plans}
            keyExtractor={(p: any) => p.plan_id}
            onRowClick={(plan: any) => handlePlanSelect(plan)}
          />
        )}
      </SectionCard>

      {/* Plan Detail Panel */}
      {selectedPlan && (
        <SectionCard
          eyebrow='Plan Details'
          title={`Plan Detail: ${selectedPlan.plan_id}`}
          status='success'
        >
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            {/* Left: Overview & Metrics */}
            <div>
              <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem' }}>Plan Overview</h4>
              
              <div style={{ margin: '1rem 0' }}>
                <span style={{ display: 'inline-block', padding: '2px 6px', background: 'var(--surface-panel)', border: '1px solid var(--surface-border)', borderRadius: '3px', fontSize: '0.65rem', color: 'var(--text-primary)' }}>
                  {selectedPlan.status}
                </span>
                <span style={{ display: 'inline-block', padding: '2px 6px', background: 'var(--surface-panel)', border: '1px solid var(--surface-border)', borderRadius: '3px', fontSize: '0.65rem', color: 'var(--text-primary)', marginLeft: '0.25rem' }}>
                  {selectedPlan.strategy}
                </span>
              </div>

              <div style={{ margin: '1rem 0' }}>
                <span style={{ display: 'inline-block', padding: '2px 6px', background: 'var(--surface-panel)', border: '1px solid var(--surface-border)', borderRadius: '3px', fontSize: '0.65rem', color: 'var(--text-primary)' }}>
                  {selectedPlan.metrics.total_delay_minutes} min delay
                </span>
                <span style={{ display: 'inline-block', padding: '2px 6px', background: 'var(--surface-panel)', border: '1px solid var(--surface-border)', borderRadius: '3px', fontSize: '0.65rem', color: 'var(--text-primary)', marginLeft: '0.25rem' }}>
                  {selectedPlan.metrics.constraints_violated} violations
                </span>
              </div>

              <div>
                <h5 style={{ margin: '0 0 0.5rem 0', fontSize: '0.75rem' }}>Blocks</h5>
                {selectedPlan.blocks.length === 0 ? (
                  <p style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>No blocks assigned</p>
                ) : (
                  <ul style={{ fontSize: '0.7rem', margin: 0, paddingLeft: '1rem' }}>
                    {selectedPlan.blocks.map((b: any, i: number) => (
                      <li key={b.block_id}>
                        {b.section_id}: {b.duration_min} min — {b.status}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>

            {/* Right: Constraints & Impact */}
            <div>
              <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem' }}>Constraint Status</h4>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                {selectedPlan.metrics.constraints_violated > 0 ? (
                  `${selectedPlan.metrics.constraints_violated} constraint${selectedPlan.metrics.constraints_violated !== 1 ? 's' : ''} violated`
                ) : 'All hard constraints satisfied'}
              </div>

              {constraintViolations.length > 0 ? (
                constraintViolations.map((cv: any, i: number) => (
                  <div key={cv.id} style={{ padding: '0.5rem 0', borderBottom: '1px solid var(--surface-border)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                      <span style={{
                        padding: '2px 6px',
                        background: cv.type === 'HARD' ? 'var(--status-critical)' : 'var(--surface-panel)',
                        border: '1px solid var(--surface-border)',
                        borderRadius: '3px',
                        fontSize: '0.65rem',
                        fontWeight: 600,
                        color: cv.type === 'HARD' ? 'var(--status-critical-fg)' : 'var(--text-primary)',
                      }}>
                        {cv.type}: {cv.name}
                      </span>
                      <span style={{
                        padding: '2px 6px',
                        background: cv.status === 'VIOLATED' ? 'var(--status-critical)' : 'var(--surface-panel)',
                        border: '1px solid var(--surface-border)',
                        borderRadius: '3px',
                        fontSize: '0.65rem',
                        color: cv.status === 'VIOLATED' ? 'var(--status-critical-fg)' : 'var(--text-primary)',
                      }}>
                        {cv.status}
                      </span>
                    </div>
                    <p style={{ fontSize: '0.65rem', color: 'var(--text-secondary)', margin: '0.25rem 0' }}>
                      {cv.description}
                    </p>
                  </div>
                ))
              ) : (
                <p style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>No constraint violations</p>
              )}

              <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--surface-border)' }}>
                <h5 style={{ margin: '0 0 0.5rem 0', fontSize: '0.75rem' }}>Train Impact</h5>
                <p style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
                  Not yet calculated — train impact analysis is owned by F06/Freebuff engine
                </p>
                <p style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
                  Affected trains will be determined by the constraint engine
                </p>
              </div>

              <div style={{ marginTop: '1rem' }}>
                <h5 style={{ margin: '0 0 0.5rem 0', fontSize: '0.75rem' }}>Provenance</h5>
                <div style={{ fontSize: '0.65rem', color: 'var(--text-secondary)' }}>
                  {selectedPlan._provenance && selectedPlan._provenance.state ? (
                    <>
                      <strong>State:</strong> {selectedPlan._provenance.state} · <strong>Source:</strong> {selectedPlan._provenance.source}
                    </>
                  ) : 'No provenance data'}
                </div>
              </div>
            </div>
          </div>
        </SectionCard>
      )}

      {/* Generate Plan Workflow */}
      {generateJob ? (
        <SectionCard eyebrow='Plan Generation' title='Plan Generation' status='success'>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
            <p>{generateJob.status === 'COMPLETED' ? 'Plan generation completed' : 'Plan generation in progress'}</p>
            {generateJob.jobId && <p>Job ID: {generateJob.jobId}</p>}
            {generateJob.status === 'FAILED' && <p style={{ color: 'var(--status-critical)' }}>Generation failed — see error log</p>}
          </div>
        </SectionCard>
      ) : (
        <Button
          variant='primary'
          size='sm'
          onClick={() => {
            // Open generate plan configuration
            const request = {
              horizon: {
                start: new Date().toISOString(),
                end: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
              },
              corridorId: 'COR-01',
              strategy: 'BALANCED',
              taskIds: plans.length > 0 ? [plans[0]?.plan_id] : undefined,
              objectiveWeights: undefined,
              scenarioContext: 'LIVE',
              idempotencyKey: `PLAN-GEN-${Date.now()}`,
            };
            handleGeneratePlan(request);
          }}
          disabled={plans.length === 0}
        >
          Generate Plan
        </Button>
      )}
    </AppShell>
  );
}

export default PlanningWorkspace;