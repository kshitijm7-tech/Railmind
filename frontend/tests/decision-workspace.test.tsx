import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import {
  buildDecisionQueue,
  canActOnRecommendation,
  findCandidatePlan,
  hasSimulationEvidence,
  summarizeConstraints,
  toDeferUntilIso,
  validateDecisionInput,
} from '../hooks/useDecisionWorkspace';
import { DEMO_RECOMMENDATION, DEMO_STATE_METADATA } from '../fixtures/demoCorridor';
import type { DecisionRecord, Plan } from '../domain';
import DecisionWorkspace from '../app/decisions/DecisionWorkspace';

vi.mock('next/navigation', () => ({
  usePathname: () => '/decisions',
}));

const mockServices = vi.hoisted(() => ({
  network: {
    getStateMetadata: vi.fn(),
    getNetwork: vi.fn(),
  },
  search: {
    search: vi.fn(),
  },
  recommendations: {
    getLatestRecommendation: vi.fn(),
    getRecommendationById: vi.fn(),
  },
  planning: {
    getPlans: vi.fn(),
    getPlanById: vi.fn(),
  },
  simulation: {
    getSimulationResult: vi.fn(),
  },
  decisions: {
    getDecisionHistory: vi.fn(),
    approveDecision: vi.fn(),
    rejectDecision: vi.fn(),
    deferDecision: vi.fn(),
  },
}));

vi.mock('../services', () => ({ services: mockServices }));
vi.mock('../services/api/serviceFactory', () => ({ getConfiguredApiMode: () => 'mock' }));

function makePlan(overrides: Partial<Plan> = {}): Plan {
  return {
    plan_id: 'PLAN-1',
    name: 'Plan 1',
    version: 1,
    state_version: 'v1024',
    strategy: 'Balanced',
    status: 'Recommended',
    blocks: [],
    metrics: {
      total_delay_minutes: 42,
      passenger_trains_affected: 3,
      goods_trains_affected: 1,
      maintenance_tasks_completed: 7,
      maintenance_tasks_unscheduled: 1,
      blocks_count: 2,
      bundled_blocks_count: 1,
      overall_overrun_risk: 0.18,
      objective_score: 0.9,
    },
    created_at: '2026-09-08T00:00:00Z' as Plan['created_at'],
    solver_runtime_ms: 1200,
    ...overrides,
  };
}

describe('useDecisionWorkspace helpers', () => {
  it('gates actions on PENDING_REVIEW only', () => {
    expect(canActOnRecommendation('PENDING_REVIEW')).toBe(true);
    expect(canActOnRecommendation('APPROVED')).toBe(false);
    expect(canActOnRecommendation('REJECTED')).toBe(false);
  });

  it('requires approver and rationale', () => {
    expect(validateDecisionInput('approve', '', '')).toMatch(/Approver/);
    expect(validateDecisionInput('approve', '', 'A. Controller')).toMatch(/Justification/);
    expect(validateDecisionInput('reject', '', 'A. Controller')).toMatch(/reason/);
    expect(validateDecisionInput('defer', 'ok', 'A. Controller')).toBeNull();
    expect(validateDecisionInput('approve', 'ok', 'A. Controller')).toBeNull();
  });

  it('summarizes constraint violations without inventing feasibility', () => {
    const summary = summarizeConstraints(DEMO_RECOMMENDATION.constraint_trace);
    expect(summary.total).toBe(DEMO_RECOMMENDATION.constraint_trace.length);
    expect(summary.violated + summary.satisfied + summary.other).toBe(summary.total);
  });

  it('builds queue from backend recommendation + history only', () => {
    const history: DecisionRecord[] = [];
    const queue = buildDecisionQueue(DEMO_RECOMMENDATION, history);
    expect(queue).toHaveLength(1);
    expect(queue[0].status).toBe(DEMO_RECOMMENDATION.status);
    expect(queue[0].planId).toBe(DEMO_RECOMMENDATION.plan_id);
  });

  it('treats null simulation as unavailable, never fake', () => {
    expect(hasSimulationEvidence(null)).toBe(false);
  });

  it('finds candidate plans without ranking', () => {
    const plans = [makePlan({ plan_id: 'PLAN-1' }), makePlan({ plan_id: 'PLAN-2' })];
    expect(findCandidatePlan(plans, 'PLAN-2')?.plan_id).toBe('PLAN-2');
    expect(findCandidatePlan(plans, 'PLAN-9')).toBeNull();
  });

  it('normalizes defer-until to UTC ISO, null when empty or invalid', () => {
    expect(toDeferUntilIso('')).toBeNull();
    expect(toDeferUntilIso('not-a-date')).toBeNull();
    const iso = toDeferUntilIso('2026-10-01T00:00');
    expect(iso).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:00\.000Z$/);
    expect(new Date(iso as string).getTime()).toBe(new Date('2026-10-01T00:00').getTime());
  });
});

describe('DecisionWorkspace', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockServices.network.getStateMetadata.mockResolvedValue(DEMO_STATE_METADATA);
    mockServices.network.getNetwork.mockResolvedValue(null);
    mockServices.search.search.mockResolvedValue([]);
    mockServices.recommendations.getLatestRecommendation.mockResolvedValue(DEMO_RECOMMENDATION);
    mockServices.planning.getPlans.mockResolvedValue([makePlan()]);
    mockServices.planning.getPlanById.mockResolvedValue(makePlan());
    mockServices.simulation.getSimulationResult.mockResolvedValue(null);
    mockServices.decisions.getDecisionHistory.mockResolvedValue([]);
    mockServices.decisions.approveDecision.mockImplementation(async (id: string) => ({
      decision_id: 'DEC-1',
      recommendation_id: DEMO_RECOMMENDATION.recommendation_id,
      plan_id: DEMO_RECOMMENDATION.plan_id,
      state_version: DEMO_RECOMMENDATION.state_version,
      action: 'APPROVE',
      authorized_by: 'A. Controller',
      user_role: 'Operations Controller',
      timestamp: '2026-09-09T00:00:00Z',
      notes: 'ok',
    }));
  });

  it('renders queue, candidate evidence, and unavailable simulation gracefully', async () => {
    render(<DecisionWorkspace />);
    expect((await screen.findAllByText(DEMO_RECOMMENDATION.headline)).length).toBeGreaterThanOrEqual(1);
    expect(await screen.findByText('Simulation evidence not available')).toBeDefined();
    expect(screen.getByText(/View plan in Planning Workspace/)).toBeDefined();
    expect(screen.getByText(/View simulation/)).toBeDefined();
    expect(screen.getByText(/Open audit trail/)).toBeDefined();
  });

  it('blocks approve without rationale and never calls backend optimistically', async () => {
    render(<DecisionWorkspace />);
    await screen.findAllByText(DEMO_RECOMMENDATION.headline);
    fireEvent.click(screen.getByRole('button', { name: /Approve Plan/ }));
    expect(await screen.findByText(/Approver name is required/)).toBeDefined();
    expect(mockServices.decisions.approveDecision).not.toHaveBeenCalled();
  });

  it('requires confirmation before submitting approval', async () => {
    render(<DecisionWorkspace />);
    await screen.findAllByText(DEMO_RECOMMENDATION.headline);
    fireEvent.change(screen.getByLabelText(/Approver name/), { target: { value: 'A. Controller' } });
    fireEvent.change(screen.getByLabelText(/Decision rationale/), { target: { value: 'Evidence reviewed.' } });
    fireEvent.click(screen.getByRole('button', { name: /^Approve Plan/ }));
    // Confirmation dialog appears; backend still untouched.
    expect(await screen.findByRole('button', { name: 'Confirm Approve' })).toBeDefined();
    expect(mockServices.decisions.approveDecision).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: /Confirm Approve/ }));
    await waitFor(() => expect(mockServices.decisions.approveDecision).toHaveBeenCalledTimes(1));
    expect(await screen.findByText(/recorded as DEC-1/)).toBeDefined();
  });

  it('sends deferUntil through the existing defer service', async () => {
    mockServices.decisions.deferDecision.mockImplementation(async (id: string, body: { deferUntil?: string }) => ({
      decision_id: 'DEC-9',
      recommendation_id: DEMO_RECOMMENDATION.recommendation_id,
      plan_id: DEMO_RECOMMENDATION.plan_id,
      state_version: DEMO_RECOMMENDATION.state_version,
      action: 'MODIFY',
      authorized_by: 'A. Controller',
      user_role: 'Operations Controller',
      timestamp: '2026-09-09T00:00:00Z',
      notes: 'deferred',
    }));
    render(<DecisionWorkspace />);
    await screen.findAllByText(DEMO_RECOMMENDATION.headline);
    fireEvent.change(screen.getByLabelText(/Approver name/), { target: { value: 'A. Controller' } });
    fireEvent.change(screen.getByLabelText(/Decision rationale/), { target: { value: 'Need more data.' } });
    fireEvent.click(screen.getByRole('button', { name: /^Defer Decision/ }));
    const input = await screen.findByLabelText(/Defer until/) as HTMLInputElement;
    fireEvent.change(input, { target: { value: '2026-10-01T00:00' } });
    fireEvent.click(screen.getByRole('button', { name: 'Confirm Defer' }));
    await waitFor(() => expect(mockServices.decisions.deferDecision).toHaveBeenCalledTimes(1));
    const body = mockServices.decisions.deferDecision.mock.calls[0][1] as { deferUntil?: string };
    expect(body.deferUntil).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:00\.000Z$/);
    expect(new Date(body.deferUntil as string).getTime()).toBe(new Date('2026-10-01T00:00').getTime());
    expect(await screen.findByText(/recorded as DEC-9/)).toBeDefined();
  });

  it('disables actions when recommendation is not pending review', async () => {
    mockServices.recommendations.getLatestRecommendation.mockResolvedValue({
      ...DEMO_RECOMMENDATION,
      status: 'APPROVED',
    });
    render(<DecisionWorkspace />);
    await screen.findAllByText(DEMO_RECOMMENDATION.headline);
    expect(screen.getByRole('button', { name: /^Approve Plan/ }).hasAttribute('disabled')).toBe(true);
    expect(screen.getByText(/no longer pending review|not PENDING_REVIEW/)).toBeDefined();
  });
});
