'use client';

import React, { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../components/layout/AppShell';
import { SectionCard } from '../../components/command-center/SectionCard';
import { Button } from '../../components/ui/Button';
import { EmptyState, ErrorState, LoadingState } from '../../components/feedback/FeedbackStates';
import { services } from '../../services';
import { getConfiguredApiMode } from '../../services/api/serviceFactory';
import { isRailmindApiError, toUserMessage } from '../../services/api/client/errors';
import type { DecisionRecord, Plan, Recommendation, SimulationResult } from '../../domain';
import type { DecisionId, PlanId } from '../../contracts/common/ids';
import type { UserRole } from '../../contracts/common/enums';
import {
  buildDecisionQueue,
  canActOnRecommendation,
  findCandidatePlan,
  hasSimulationEvidence,
  summarizeConstraints,
  validateDecisionInput,
  type DecisionAction,
} from '../../hooks/useDecisionWorkspace';

type LoadPhase = 'idle' | 'loading' | 'success' | 'error';

const ACTION_LABEL: Record<DecisionAction, string> = {
  approve: 'Approve',
  reject: 'Reject',
  defer: 'Defer',
};

function DecisionWorkspace() {
  const apiMode = getConfiguredApiMode();

  const [phase, setPhase] = useState<LoadPhase>('idle');
  const [loadError, setLoadError] = useState<string | null>(null);
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [candidatePlan, setCandidatePlan] = useState<Plan | null>(null);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [simulation, setSimulation] = useState<SimulationResult | null>(null);
  const [history, setHistory] = useState<DecisionRecord[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const [rationale, setRationale] = useState('');
  const [approver, setApprover] = useState('');
  const [role, setRole] = useState<UserRole>('Operations Controller');

  const [pendingAction, setPendingAction] = useState<DecisionAction | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  const load = useCallback(async () => {
    setPhase('loading');
    setLoadError(null);
    try {
      const [rec, planList, hist] = await Promise.all([
        services.recommendations.getLatestRecommendation(),
        services.planning.getPlans(),
        services.decisions.getDecisionHistory(),
      ]);
      setRecommendation(rec);
      setPlans(planList);
      setHistory(hist);
      if (rec) {
        setSelectedId(rec.recommendation_id);
        const direct = findCandidatePlan(planList, rec.plan_id);
        if (direct) {
          setCandidatePlan(direct);
        } else {
          const fetched = await services.planning.getPlanById(rec.plan_id as PlanId);
          setCandidatePlan(fetched);
        }
        try {
          const sim = await services.simulation.getSimulationResult(rec.plan_id);
          setSimulation(sim);
        } catch {
          setSimulation(null);
        }
      }
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

  const queue = buildDecisionQueue(recommendation, history);
  const actionable = recommendation ? canActOnRecommendation(recommendation.status) : false;
  const constraints = recommendation ? summarizeConstraints(recommendation.constraint_trace) : null;
  const selectedIsRecommendation = recommendation !== null && selectedId === recommendation.recommendation_id;

  const requestAction = (action: DecisionAction) => {
    setActionError(null);
    setActionSuccess(null);
    const validation = validateDecisionInput(action, rationale, approver);
    if (validation) {
      setActionError(validation);
      return;
    }
    if (!actionable) {
      setActionError('This decision is no longer pending review. Refresh to see backend state.');
      return;
    }
    setPendingAction(action);
  };

  const confirmAction = async () => {
    if (!pendingAction || !recommendation || submitting) return;
    setSubmitting(true);
    setActionError(null);
    try {
      const decisionId = recommendation.recommendation_id as DecisionId;
      const trimmedRationale = rationale.trim();
      const trimmedApprover = approver.trim();
      let record: DecisionRecord;
      if (pendingAction === 'approve') {
        record = await services.decisions.approveDecision(decisionId, {
          approver: trimmedApprover,
          role,
          justification: trimmedRationale,
        });
      } else if (pendingAction === 'reject') {
        record = await services.decisions.rejectDecision(decisionId, {
          approver: trimmedApprover,
          role,
          reason: trimmedRationale,
        });
      } else {
        record = await services.decisions.deferDecision(decisionId, {
          approver: trimmedApprover,
          role,
          reason: trimmedRationale,
        });
      }
      const refreshed = await services.decisions.getDecisionHistory();
      setHistory(refreshed);
      setActionSuccess(
        `${ACTION_LABEL[pendingAction]} recorded as ${record.decision_id} via ${apiMode.toUpperCase()} service.`,
      );
      setPendingAction(null);
      setRationale('');
    } catch (error: unknown) {
      if (isRailmindApiError(error) && error.kind === 'CONFLICT') {
        setActionError('Decision conflicts with current backend state (possibly decided by another user). History refreshed — review before retrying.');
        try {
          setHistory(await services.decisions.getDecisionHistory());
        } catch {
          // History refresh is best-effort; the conflict message stands.
        }
      } else {
        setActionError(toUserMessage(error));
      }
      setPendingAction(null);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AppShell
      title="Decision Workspace"
      eyebrow="Governed human decision — system proposes, human disposes"
    >
      <div style={{ marginBottom: '1.5rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
        Review planning evidence, then approve, reject, or defer. The frontend never decides autonomously;
        every action is confirmed by you and governed by the backend.
        <span style={{ marginLeft: '0.5rem', fontFamily: 'var(--font-mono)', fontSize: '0.72rem' }}>
          Source: {apiMode.toUpperCase()}
        </span>
      </div>

      {phase === 'loading' && <LoadingState message="Loading decision queue…" />}
      {phase === 'error' && (
        <ErrorState title="Decision queue unavailable" error={loadError ?? undefined} affectedScope="Decision workspace" onRetry={() => void load()} />
      )}

      {phase === 'success' && (
        <>
          <SectionCard eyebrow="Decision Queue" title={`Decisions requiring review (${queue.length})`} status="success">
            {queue.length === 0 ? (
              <EmptyState title="No decisions currently require review." description="No recommendations or recorded decisions were returned by the backend." />
            ) : (
              <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {queue.map((item) => {
                  const selected = item.id === selectedId;
                  return (
                    <li key={`${item.kind}-${item.id}`}>
                      <button
                        type="button"
                        onClick={() => setSelectedId(item.id)}
                        aria-pressed={selected}
                        style={{
                          width: '100%',
                          textAlign: 'left',
                          background: selected ? 'var(--surface-elevated)' : 'var(--surface-panel)',
                          border: selected ? '1px solid var(--text-accent)' : '1px solid var(--surface-border)',
                          borderRadius: 'var(--radius-sm)',
                          padding: '0.6rem 0.8rem',
                          cursor: 'pointer',
                          color: 'var(--text-primary)',
                        }}
                      >
                        <span style={{ fontSize: '0.7rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                          [{item.kind.toUpperCase()}] {item.status}
                        </span>
                        <span style={{ display: 'block', fontWeight: 600, fontSize: '0.85rem' }}>{item.title}</span>
                        <span style={{ display: 'block', fontSize: '0.72rem', color: 'var(--text-secondary)' }}>
                          Plan {item.planId} · {item.detail}
                        </span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            )}
          </SectionCard>

          {!recommendation && (
            <SectionCard eyebrow="Decision Detail" title="This decision could not be loaded." status="success">
              <EmptyState title="Supporting evidence is not available." description="The backend returned no pending recommendation." />
            </SectionCard>
          )}

          {recommendation && !selectedIsRecommendation && (
            <SectionCard eyebrow="Decision Detail" title="Recorded decision" status="success">
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Select the pending recommendation in the queue to review evidence and act. Recorded history
                entries are immutable — use the audit trail for full context.{' '}
                <Link href="/audit">Open audit trail</Link>.
              </p>
            </SectionCard>
          )}

          {recommendation && selectedIsRecommendation && (
            <>
              <SectionCard eyebrow="Decision Header" title={recommendation.headline} status="success">
                <dl style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.5rem', fontSize: '0.8rem', margin: 0 }}>
                  <div><dt style={{ color: 'var(--text-muted)' }}>Recommendation</dt><dd style={{ margin: 0, fontFamily: 'var(--font-mono)' }}>{recommendation.recommendation_id}</dd></div>
                  <div><dt style={{ color: 'var(--text-muted)' }}>Status</dt><dd style={{ margin: 0 }}>{recommendation.status}</dd></div>
                  <div><dt style={{ color: 'var(--text-muted)' }}>Candidate plan</dt><dd style={{ margin: 0, fontFamily: 'var(--font-mono)' }}>{recommendation.plan_id}</dd></div>
                  <div><dt style={{ color: 'var(--text-muted)' }}>State version</dt><dd style={{ margin: 0, fontFamily: 'var(--font-mono)' }}>{recommendation.state_version}</dd></div>
                </dl>
              </SectionCard>

              <SectionCard eyebrow="Decision Context" title="What is being decided" status="success">
                <p style={{ fontSize: '0.85rem', color: 'var(--text-primary)' }}>{recommendation.action_summary}</p>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>{recommendation.primary_rationale}</p>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Evidence hierarchy: backend decision data → planning engine results → constraint results →
                  simulation results → human rationale. Frontend values are never authoritative.
                </p>
              </SectionCard>

              <SectionCard eyebrow="Candidate Plan" title={`Plan ${recommendation.plan_id}`} status="success">
                {candidatePlan ? (
                  <dl style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.5rem', fontSize: '0.8rem', margin: 0 }}>
                    <div><dt style={{ color: 'var(--text-muted)' }}>Name</dt><dd style={{ margin: 0 }}>{candidatePlan.name}</dd></div>
                    <div><dt style={{ color: 'var(--text-muted)' }}>Status</dt><dd style={{ margin: 0 }}>{candidatePlan.status}</dd></div>
                    <div><dt style={{ color: 'var(--text-muted)' }}>Strategy</dt><dd style={{ margin: 0 }}>{candidatePlan.strategy}</dd></div>
                    <div><dt style={{ color: 'var(--text-muted)' }}>Total delay</dt><dd style={{ margin: 0 }}>{candidatePlan.metrics.total_delay_minutes} min</dd></div>
                    <div><dt style={{ color: 'var(--text-muted)' }}>Maintenance cleared</dt><dd style={{ margin: 0 }}>{candidatePlan.metrics.maintenance_tasks_completed} tasks</dd></div>
                    <div><dt style={{ color: 'var(--text-muted)' }}>Overrun risk</dt><dd style={{ margin: 0 }}>{Math.round(candidatePlan.metrics.overall_overrun_risk * 100)}%</dd></div>
                    <div><dt style={{ color: 'var(--text-muted)' }}>Provenance</dt><dd style={{ margin: 0 }}>{apiMode.toUpperCase()}</dd></div>
                  </dl>
                ) : (
                  <EmptyState title="Supporting evidence is not available." description="Candidate plan details were not returned for this recommendation." />
                )}
                <p style={{ fontSize: '0.78rem' }}>
                  <Link href="/planning">View plan in Planning Workspace</Link>
                </p>
              </SectionCard>

              <SectionCard eyebrow="Alternatives" title={`Other candidates (${recommendation.alternatives.length})`} status="success">
                {recommendation.alternatives.length === 0 ? (
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>No alternatives provided by the backend.</p>
                ) : (
                  <ul style={{ fontSize: '0.82rem', color: 'var(--text-primary)', paddingLeft: '1.1rem', margin: '0.25rem 0' }}>
                    {recommendation.alternatives.map((alt) => (
                      <li key={alt.plan_id}>
                        <strong>{alt.name}</strong> ({alt.strategy}): {alt.delay_delta_min > 0 ? `+${alt.delay_delta_min}` : alt.delay_delta_min}m delay,{' '}
                        {alt.risk_delta_pct > 0 ? `+${alt.risk_delta_pct}` : alt.risk_delta_pct}% risk
                      </li>
                    ))}
                  </ul>
                )}
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  The frontend does not rank alternatives. Ranks shown are backend-provided only.
                </p>
              </SectionCard>

              <SectionCard eyebrow="Constraint Evidence" title={constraints && constraints.hasViolation ? 'Hard violation present' : 'Constraints'} status="success">
                {constraints && constraints.hasViolation && (
                  <p role="alert" style={{ background: 'var(--status-critical-bg)', border: '1px solid var(--status-critical)', color: 'var(--status-critical)', borderRadius: 'var(--radius-sm)', padding: '0.6rem 0.8rem', fontSize: '0.82rem', fontWeight: 700 }}>
                    HARD CONSTRAINT VIOLATION — {constraints.violated} violated of {constraints.total} traced. This is not an ordinary warning.
                  </p>
                )}
                <ul style={{ fontSize: '0.8rem', paddingLeft: '1.1rem', margin: '0.5rem 0' }}>
                  {recommendation.constraint_trace.map((item) => (
                    <li key={item.constraint_name} style={{ color: item.status === 'VIOLATED' ? 'var(--status-critical)' : 'var(--text-primary)' }}>
                      <strong>[{item.status}]</strong> {item.constraint_name} ({item.category}) — {item.details}
                    </li>
                  ))}
                </ul>
              </SectionCard>

              <SectionCard eyebrow="Simulation Evidence" title="Baseline vs scenario" status="success">
                {hasSimulationEvidence(simulation) && simulation ? (
                  <dl style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.5rem', fontSize: '0.8rem', margin: 0 }}>
                    <div><dt style={{ color: 'var(--text-muted)' }}>Scenario</dt><dd style={{ margin: 0, fontFamily: 'var(--font-mono)' }}>{simulation.scenario_id}</dd></div>
                    <div><dt style={{ color: 'var(--text-muted)' }}>Total delay</dt><dd style={{ margin: 0 }}>{simulation.total_delay_minutes} min</dd></div>
                    <div><dt style={{ color: 'var(--text-muted)' }}>Affected trains</dt><dd style={{ margin: 0 }}>{simulation.affected_train_ids.join(', ') || '—'}</dd></div>
                    <div><dt style={{ color: 'var(--text-muted)' }}>Completion rate</dt><dd style={{ margin: 0 }}>{Math.round(simulation.maintenance_completion_rate * 100)}%</dd></div>
                    <div><dt style={{ color: 'var(--text-muted)' }}>Risk level</dt><dd style={{ margin: 0 }}>{simulation.risk_level}</dd></div>
                  </dl>
                ) : (
                  <EmptyState title="Simulation evidence not available" description="Simulation evidence unavailable — the F06 workspace is incomplete and no result was returned through the service interface. This does not imply approval." />
                )}
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Simulation evidence is analytical only and never implies approval. <Link href="/simulation">View simulation</Link>.
                </p>
              </SectionCard>

              <SectionCard eyebrow="Risk Evidence" title="Risk" status="success">
                <p style={{ fontSize: '0.82rem', color: 'var(--text-primary)' }}>
                  Backend overrun risk: {recommendation.expected_outcome.overrun_risk_pct}% · Plan Monte Carlo:{' '}
                  {candidatePlan ? `${Math.round(candidatePlan.metrics.overall_overrun_risk * 100)}%` : 'not available'}
                </p>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Risk is displayed only as provided by the backend. The frontend calculates no risk.
                </p>
              </SectionCard>

              <SectionCard eyebrow="Decision Rationale" title="Human input" status="success">
                <label htmlFor="f07-approver" style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, marginBottom: '0.25rem' }}>
                  Approver name
                </label>
                <input
                  id="f07-approver"
                  type="text"
                  value={approver}
                  onChange={(e) => setApprover(e.target.value)}
                  placeholder="e.g. Senior Operations Controller"
                  style={{ width: '100%', maxWidth: '24rem', padding: '0.45rem 0.6rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--surface-border)', background: 'var(--surface-base)', color: 'var(--text-primary)' }}
                />
                <label htmlFor="f07-role" style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, margin: '0.75rem 0 0.25rem 0' }}>
                  Role
                </label>
                <select
                  id="f07-role"
                  value={role}
                  onChange={(e) => setRole(e.target.value as UserRole)}
                  style={{ padding: '0.45rem 0.6rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--surface-border)', background: 'var(--surface-base)', color: 'var(--text-primary)' }}
                >
                  <option value="Operations Controller">Operations Controller</option>
                  <option value="Planning Officer">Planning Officer</option>
                  <option value="Senior Divisional Engineer">Senior Divisional Engineer</option>
                </select>
                <label htmlFor="f07-rationale" style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, margin: '0.75rem 0 0.25rem 0' }}>
                  Decision rationale (required)
                </label>
                <textarea
                  id="f07-rationale"
                  value={rationale}
                  onChange={(e) => setRationale(e.target.value)}
                  rows={4}
                  placeholder="Approve: why this candidate is accepted. Reject: why it is rejected. Defer: why postponement is required."
                  style={{ width: '100%', padding: '0.5rem 0.6rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--surface-border)', background: 'var(--surface-base)', color: 'var(--text-primary)', fontSize: '0.82rem' }}
                />
              </SectionCard>

              <SectionCard eyebrow="Decision Actions" title="Approve · Reject · Defer" status="success">
                {!actionable && (
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    Actions disabled: recommendation status is {recommendation.status}, not PENDING_REVIEW.
                  </p>
                )}
                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                  <Button variant="primary" size="sm" disabled={!actionable || submitting} onClick={() => requestAction('approve')}>
                    {submitting && pendingAction === 'approve' ? 'Submitting…' : 'Approve Plan'}
                  </Button>
                  <Button variant="danger" size="sm" disabled={!actionable || submitting} onClick={() => requestAction('reject')}>
                    {submitting ? 'Submitting…' : 'Reject Candidate'}
                  </Button>
                  <Button variant="secondary" size="sm" disabled={!actionable || submitting} onClick={() => requestAction('defer')}>
                    {submitting ? 'Submitting…' : 'Defer Decision'}
                  </Button>
                </div>
                {actionError && (
                  <p role="alert" style={{ color: 'var(--status-critical)', fontSize: '0.8rem' }}>{actionError}</p>
                )}
                {actionSuccess && (
                  <p role="status" style={{ color: '#22c55e', fontSize: '0.8rem' }}>
                    {actionSuccess} <Link href="/audit">Open audit trail</Link>.
                  </p>
                )}
                {pendingAction && (
                  <div role="dialog" aria-modal="true" aria-labelledby="f07-confirm-title" style={{ marginTop: '0.75rem', border: '1px solid var(--surface-border-strong)', borderRadius: 'var(--radius-sm)', padding: '0.9rem 1rem', background: 'var(--surface-elevated)' }}>
                    <h4 id="f07-confirm-title" style={{ margin: '0 0 0.4rem 0' }}>
                      Confirm {ACTION_LABEL[pendingAction]}?
                    </h4>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', margin: '0 0 0.6rem 0' }}>
                      Recommendation {recommendation.recommendation_id} · Candidate {recommendation.plan_id}. You are
                      submitting this action for the next governed stage.
                      This will be recorded in the decision history. The plan is not executed by this action.
                    </p>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <Button variant="secondary" size="sm" disabled={submitting} onClick={() => setPendingAction(null)}>
                        Cancel
                      </Button>
                      <Button
                        variant={pendingAction === 'reject' ? 'danger' : 'primary'}
                        size="sm"
                        disabled={submitting}
                        onClick={() => void confirmAction()}
                      >
                        {submitting ? 'Submitting…' : `Confirm ${ACTION_LABEL[pendingAction]}`}
                      </Button>
                    </div>
                  </div>
                )}
              </SectionCard>
            </>
          )}

          <SectionCard eyebrow="Decision History" title={`Audit history (${history.length})`} status="success">
            {history.length === 0 ? (
              <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>No authorization actions submitted yet during this session.</p>
            ) : (
              <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                {history.map((d) => (
                  <li key={d.decision_id} style={{ fontSize: '0.78rem', border: '1px solid var(--surface-border)', borderRadius: 'var(--radius-sm)', padding: '0.5rem 0.7rem' }}>
                    <strong>{d.action}</strong> · Plan {d.plan_id} · {d.decision_id} · {d.authorized_by} ({d.user_role})
                  </li>
                ))}
              </ul>
            )}
            <p style={{ fontSize: '0.78rem' }}>
              <Link href="/audit">Open audit trail</Link> · <Link href="/">Back to Command Center</Link>
            </p>
          </SectionCard>
        </>
      )}
    </AppShell>
  );
}

export default DecisionWorkspace;
