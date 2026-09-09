import type { DecisionRecord, Plan, Recommendation, SimulationResult } from '../domain';
import { makeTimestamp, type ISOTimestamp } from '../contracts/common/ids';

export type DecisionAction = 'approve' | 'reject' | 'defer';

/** Backend is authoritative: only PENDING_REVIEW recommendations accept actions. */
export function canActOnRecommendation(status: Recommendation['status']): boolean {
  return status === 'PENDING_REVIEW';
}

/**
 * Validate human input before any submission.
 * Returns a safe user-facing message, or null when valid.
 * Contract mapping: approve -> justification (required),
 * reject/defer -> reason (required), approver always required.
 */
export function validateDecisionInput(
  action: DecisionAction,
  rationale: string,
  approver: string,
): string | null {
  if (approver.trim().length === 0) return 'Approver name is required.';
  if (rationale.trim().length === 0) {
    return action === 'approve'
      ? 'Justification is required to approve.'
      : 'A reason is required.';
  }
  return null;
}

export interface ConstraintSummary {
  total: number;
  violated: number;
  satisfied: number;
  other: number;
  hasViolation: boolean;
}

/** Pure summary over backend constraint trace. No feasibility is invented. */
export function summarizeConstraints(
  trace: Recommendation['constraint_trace'],
): ConstraintSummary {
  let violated = 0;
  let satisfied = 0;
  for (const item of trace) {
    if (item.status === 'VIOLATED') violated += 1;
    else if (item.status === 'SATISFIED') satisfied += 1;
  }
  const total = trace.length;
  return { total, violated, satisfied, other: total - violated - satisfied, hasViolation: violated > 0 };
}

export interface DecisionQueueItem {
  id: string;
  kind: 'recommendation' | 'decision';
  title: string;
  status: string;
  planId: string;
  detail: string;
}

/**
 * Queue view-model: pending recommendation first, then backend decision history.
 * Only surfaces states from the domain contracts — nothing invented.
 */
export function buildDecisionQueue(
  recommendation: Recommendation | null,
  history: DecisionRecord[],
): DecisionQueueItem[] {
  const items: DecisionQueueItem[] = [];
  if (recommendation) {
    items.push({
      id: recommendation.recommendation_id,
      kind: 'recommendation',
      title: recommendation.headline,
      status: recommendation.status,
      planId: recommendation.plan_id,
      detail: `State ${recommendation.state_version} · Engine ${recommendation.model_version}`,
    });
  }
  for (const record of history) {
    items.push({
      id: record.decision_id,
      kind: 'decision',
      title: `${record.action} — Plan ${record.plan_id}`,
      status: record.action,
      planId: record.plan_id,
      detail: `By ${record.authorized_by} (${record.user_role})`,
    });
  }
  return items;
}

/** Simulation evidence is analytical only; null means unavailable, never fake. */
export function hasSimulationEvidence(result: SimulationResult | null): boolean {
  return result !== null;
}

/** Candidate lookup from already-fetched plans. No ranking is performed here. */
export function findCandidatePlan(plans: Plan[], planId: string): Plan | null {
  return plans.find((p) => p.plan_id === planId) ?? null;
}

/**
 * Normalize an HTML datetime-local value to a contract ISOTimestamp (UTC ISO),
 * or null when empty/invalid. The field is optional — absence means no
 * deferred-until date is sent.
 */
export function toDeferUntilIso(value: string): ISOTimestamp | null {
  const trimmed = value.trim();
  if (trimmed.length === 0) return null;
  const millis = Date.parse(trimmed);
  if (Number.isNaN(millis)) return null;
  return makeTimestamp(new Date(millis).toISOString());
}
