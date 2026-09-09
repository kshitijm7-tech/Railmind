'use client';

import React, { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../components/layout/AppShell';
import { SectionCard } from '../../components/command-center/SectionCard';
import { Button } from '../../components/ui/Button';
import { StateBadge } from '../../components/state/StateBadge';
import { EmptyState, ErrorState, LoadingState } from '../../components/feedback/FeedbackStates';
import { services } from '../../services';
import { getConfiguredApiMode } from '../../services/api/serviceFactory';
import { toUserMessage } from '../../services/api/client/errors';
import { useOperationalContext } from '../../context/OperationalContext';
import type { Plan, Scenario, SimulationResult } from '../../domain';
import {
  buildRunRequest,
  hasUsableResult,
  selectDefaults,
  summarizeSimulation,
} from '../../hooks/useSimulationWorkspace';
import { SimulationImpactDiagram } from '../../components/railway/SimulationImpactDiagram';

type LoadPhase = 'idle' | 'loading' | 'success' | 'error';
type RunPhase = 'idle' | 'running' | 'done' | 'error';

const POLL_ATTEMPTS = 8;
const POLL_INTERVAL_MS = 1500;

function wait(ms: number): Promise<void> {
  return new Promise((resolve) => { setTimeout(resolve, ms); });
}

function SimulationWorkspace() {
  const apiMode = getConfiguredApiMode();
  const { enterScenario, activeScenario } = useOperationalContext();

  const [phase, setPhase] = useState<LoadPhase>('idle');
  const [loadError, setLoadError] = useState<string | null>(null);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [selectedPlanId, setSelectedPlanId] = useState<string | null>(null);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string | null>(null);

  const [runPhase, setRunPhase] = useState<RunPhase>('idle');
  const [runJobId, setRunJobId] = useState<string | null>(null);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [runError, setRunError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setPhase('loading');
    setLoadError(null);
    try {
      const [scenarioList, planList] = await Promise.all([
        services.simulation.getScenarios(),
        services.planning.getPlans(),
      ]);
      setScenarios(scenarioList);
      setPlans(planList);
      const defaults = selectDefaults(scenarioList, planList);

      let targetPlanId = defaults.planId;
      if (typeof window !== 'undefined') {
        const params = new URLSearchParams(window.location.search);
        const qPlanId = params.get('planId');
        if (qPlanId && planList.some(p => p.plan_id === qPlanId)) {
          targetPlanId = qPlanId;
        }
      }

      setSelectedPlanId((prev) => prev ?? targetPlanId);
      setSelectedScenarioId((prev) => prev ?? defaults.scenarioId);
      setPhase('success');
    } catch (error: unknown) {
      setLoadError(toUserMessage(error));
      setPhase('error');
    }
  }, []);

  useEffect(() => {
    // Initial governed data load on mount; user retry reuses the same loader.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load();
  }, [load]);

  const runSimulation = useCallback(async () => {
    if (!selectedPlanId || !selectedScenarioId) {
      setRunError('Select a plan and a scenario before running a simulation.');
      setRunPhase('error');
      return;
    }
    setRunPhase('running');
    setRunError(null);
    setResult(null);
    try {
      const job = await services.simulation.runSimulation(buildRunRequest(selectedPlanId, selectedScenarioId));
      setRunJobId(job.jobId);
      let payload: SimulationResult | null = null;
      for (let attempt = 0; attempt < POLL_ATTEMPTS; attempt += 1) {
        payload = await services.simulation.getSimulationResult(job.jobId);
        if (hasUsableResult(payload)) break;
        await wait(POLL_INTERVAL_MS);
      }
      if (!hasUsableResult(payload)) {
        setRunError('Simulation result is not available yet. Retry shortly — no result is fabricated.');
        setRunPhase('error');
        return;
      }
      setResult(payload);
      setRunPhase('done');
    } catch (error: unknown) {
      setRunError(toUserMessage(error));
      setRunPhase('error');
    }
  }, [selectedPlanId, selectedScenarioId]);

  const dismissRun = useCallback(() => {
    setRunPhase('idle');
    setRunJobId(null);
    setResult(null);
    setRunError(null);
  }, []);

  const summary = result ? summarizeSimulation(result) : null;
  const running = runPhase === 'running';

  return (
    <AppShell
      title="Simulation & What-If Analysis"
      eyebrow="What-if scenario analysis — system generated, human reviewed"
      actions={<StateBadge stateType="SCENARIO" label="COPY-ON-WRITE BRANCHING" />}
    >
      <div style={{ marginBottom: '1.5rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
        Evaluate impact propagation, duration overruns, and unexpected track closures without
        mutating live operational state. Simulation output is analytical evidence only.
        <span style={{ marginLeft: '0.5rem', fontFamily: 'var(--font-mono)', fontSize: '0.72rem' }}>
          Source: {apiMode.toUpperCase()}
        </span>
      </div>

      {phase === 'loading' && <LoadingState message="Loading simulation scenarios…" />}
      {phase === 'error' && (
        <ErrorState title="Simulation workspace unavailable" error={loadError ?? undefined} affectedScope="Simulation workspace" onRetry={() => void load()} />
      )}

      {phase === 'success' && (
        <>
          <SectionCard eyebrow="Scenarios" title={`What-if scenario branches (${scenarios.length})`} status="success">
            {scenarios.length === 0 ? (
              <EmptyState
                title="No simulation scenarios"
                description="No simulation scenarios available. Create a scenario from a plan to begin what-if analysis."
              />
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
                {scenarios.map((sc) => {
                  const isActive = activeScenario?.scenario_id === sc.scenario_id;
                  const isSelected = selectedScenarioId === sc.scenario_id;
                  return (
                    <div
                      key={sc.scenario_id}
                      style={{
                        background: 'var(--surface-panel)',
                        border: isActive ? '1px solid var(--state-scenario)' : '1px solid var(--surface-border)',
                        borderRadius: 'var(--radius-md)',
                        padding: '1rem',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '0.5rem',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <StateBadge stateType="SCENARIO" label={sc.scenario_type} />
                        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Base: {sc.base_state_version}</span>
                      </div>
                      <h3 style={{ margin: 0, fontSize: '0.95rem', color: 'var(--text-primary)' }}>{sc.name}</h3>
                      <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.78rem', lineHeight: 1.4 }}>{sc.description}</p>
                      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.25rem', flexWrap: 'wrap' }}>
                        <Button variant={isSelected ? 'primary' : 'secondary'} size="sm" onClick={() => setSelectedScenarioId(sc.scenario_id)}>
                          {isSelected ? '✓ Selected for simulation' : 'Select for simulation'}
                        </Button>
                        <Button variant={isActive ? 'outline' : 'ghost'} size="sm" onClick={() => enterScenario(sc)}>
                          {isActive ? '✓ Active branch' : 'Enter branch'}
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </SectionCard>

          <SectionCard eyebrow="Run Simulation" title="Plan under test" status="success">
            {plans.length === 0 ? (
              <EmptyState
                title="No plans available"
                description="No plans available for simulation. Generate plans from the Block Planning Workspace first."
              />
            ) : (
              <>
                <label htmlFor="f06-plan" style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, marginBottom: '0.25rem' }}>
                  Candidate plan
                </label>
                <select
                  id="f06-plan"
                  value={selectedPlanId ?? ''}
                  onChange={(e) => setSelectedPlanId(e.target.value || null)}
                  style={{ width: '100%', maxWidth: '28rem', padding: '0.45rem 0.6rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--surface-border)', background: 'var(--surface-base)', color: 'var(--text-primary)' }}
                >
                  {plans.map((p) => (
                    <option key={p.plan_id} value={p.plan_id}>
                      {p.name} ({p.plan_id} · {p.status})
                    </option>
                  ))}
                </select>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Scenario: {selectedScenarioId ?? 'none selected'} · Request carries an explicit SCENARIO boundary.
                </p>
                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                  <Button variant="primary" size="sm" disabled={running || !selectedPlanId || !selectedScenarioId} onClick={() => void runSimulation()}>
                    {running ? 'Simulating…' : 'Run Simulation'}
                  </Button>
                  {(runPhase === 'done' || runPhase === 'error') && (
                    <Button variant="secondary" size="sm" disabled={running} onClick={dismissRun}>
                      Dismiss
                    </Button>
                  )}
                </div>
              </>
            )}
            <p style={{ fontSize: '0.78rem' }}>
              <Link href="/planning">Generate plans in Planning Workspace</Link>
            </p>
          </SectionCard>

          {/* Simulation Impact & Propagation Flow Diagram */}
          <SimulationImpactDiagram
            plan={plans.find(p => p.plan_id === selectedPlanId) ?? null}
            scenario={scenarios.find(s => s.scenario_id === selectedScenarioId) ?? null}
            result={result}
          />

          {(runPhase === 'running' || runPhase === 'done' || runPhase === 'error') && (
            <SectionCard
              eyebrow="Simulation Results"
              title={runJobId ? `Simulation ${runJobId}` : 'Simulation'}
              status={runPhase === 'error' ? 'error' : 'success'}
              errorMessage={runPhase === 'error' ? runError : null}
              onRetry={runPhase === 'error' ? () => void runSimulation() : undefined}
            >
              {runPhase === 'running' && <LoadingState message="Simulation running — polling backend for the result…" />}
              {runPhase === 'done' && summary && result && (
                <div style={{ fontSize: '0.85rem' }}>
                  <dl style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.5rem', margin: 0 }}>
                    <div><dt style={{ color: 'var(--text-muted)' }}>Total delay</dt><dd style={{ margin: 0 }}>{summary.delayMinutes} min</dd></div>
                    <div><dt style={{ color: 'var(--text-muted)' }}>Affected trains</dt><dd style={{ margin: 0 }}>{summary.affectedTrains.join(', ') || '—'}</dd></div>
                    <div><dt style={{ color: 'var(--text-muted)' }}>Affected blocks</dt><dd style={{ margin: 0 }}>{summary.affectedBlocks.join(', ') || '—'}</dd></div>
                    <div><dt style={{ color: 'var(--text-muted)' }}>Maintenance completion</dt><dd style={{ margin: 0 }}>{summary.completionPct}%</dd></div>
                    <div><dt style={{ color: 'var(--text-muted)' }}>Overrun probability</dt><dd style={{ margin: 0 }}>{summary.overrunProbabilityPct}%</dd></div>
                    <div><dt style={{ color: 'var(--text-muted)' }}>Risk level</dt><dd style={{ margin: 0 }}>{summary.riskLevel}</dd></div>
                  </dl>
                  <div style={{ marginTop: '0.75rem', padding: '0.6rem 0.8rem', background: 'var(--surface-panel)', border: '1px solid var(--surface-border)', borderRadius: 'var(--radius-sm)' }}>
                    <p style={{ margin: '0 0 0.35rem 0', fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                      Monte Carlo · {summary.iterations} iterations
                    </p>
                    <ul style={{ margin: 0, paddingLeft: '1.1rem', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                      <li>Expected mean delay: {summary.expectedMeanDelayMin} min</li>
                      <li>P90 delay: {summary.p90DelayMin} min</li>
                    </ul>
                  </div>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Analytical evidence only — it never implies plan approval. <Link href="/decisions">Review in Decision Workspace</Link>.
                  </p>
                </div>
              )}
            </SectionCard>
          )}
        </>
      )}
    </AppShell>
  );
}

export default SimulationWorkspace;
