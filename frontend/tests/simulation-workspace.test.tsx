import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import {
  buildRunRequest,
  hasUsableResult,
  selectDefaults,
  summarizeSimulation,
} from '../hooks/useSimulationWorkspace';
import { DEMO_PLANS, DEMO_SCENARIOS, DEMO_STATE_METADATA } from '../fixtures/demoCorridor';
import type { SimulationResult } from '../domain';
import SimulationWorkspace from '../app/simulation/SimulationWorkspace';

vi.mock('next/navigation', () => ({
  usePathname: () => '/simulation',
}));

const mockServices = vi.hoisted(() => ({
  network: {
    getStateMetadata: vi.fn(),
    getNetwork: vi.fn(),
  },
  search: {
    search: vi.fn(),
  },
  simulation: {
    getScenarios: vi.fn(),
    runSimulation: vi.fn(),
    getSimulationResult: vi.fn(),
  },
  planning: {
    getPlans: vi.fn(),
    getPlanById: vi.fn(),
  },
}));

vi.mock('../services', () => ({ services: mockServices }));
vi.mock('../services/api/serviceFactory', () => ({ getConfiguredApiMode: () => 'mock' }));

const DEMO_RESULT: SimulationResult = {
  simulation_id: 'SIM-1',
  scenario_id: 'SCN-WHATIF-01',
  plan_id: 'PLAN-OPT-01',
  total_delay_minutes: 48,
  affected_train_ids: ['TRN-12001'],
  affected_block_ids: ['BLK-04-01'],
  maintenance_completion_rate: 0.75,
  monte_carlo: {
    iterations: 200,
    p_any_violation: 0.38,
    p_overrun_by_block: { 'BLK-04-01': 0.38 },
    expected_mean_delay_min: 44.5,
    p90_delay_min: 62.0,
  },
  risk_level: 'HIGH',
};

describe('useSimulationWorkspace helpers', () => {
  it('builds governed requests inside an explicit SCENARIO boundary', () => {
    const request = buildRunRequest('PLAN-OPT-01', 'SCN-WHATIF-01');
    expect(request.planId).toBe('PLAN-OPT-01');
    expect(request.scenarioId).toBe('SCN-WHATIF-01');
    expect(request.scenarioContext.mode).toBe('SCENARIO');
    expect(request.scenarioContext.scenarioId).toBe('SCN-WHATIF-01');
  });

  it('projects backend output without inventing values', () => {
    const summary = summarizeSimulation(DEMO_RESULT);
    expect(summary.delayMinutes).toBe(48);
    expect(summary.completionPct).toBe(75);
    expect(summary.overrunProbabilityPct).toBe(38);
    expect(summary.riskLevel).toBe('HIGH');
    expect(summary.affectedTrains).toEqual(['TRN-12001']);
  });

  it('defaults to first-available entries, null when empty', () => {
    expect(selectDefaults(DEMO_SCENARIOS, DEMO_PLANS)).toEqual({
      planId: 'PLAN-OPT-01',
      scenarioId: 'SCN-WHATIF-01',
    });
    expect(selectDefaults([], [])).toEqual({ planId: null, scenarioId: null });
  });

  it('treats null results as unavailable, never fake', () => {
    expect(hasUsableResult(null)).toBe(false);
    expect(hasUsableResult(DEMO_RESULT)).toBe(true);
  });
});

describe('SimulationWorkspace', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockServices.network.getStateMetadata.mockResolvedValue(DEMO_STATE_METADATA);
    mockServices.network.getNetwork.mockResolvedValue(null);
    mockServices.search.search.mockResolvedValue([]);
    mockServices.simulation.getScenarios.mockResolvedValue(DEMO_SCENARIOS);
    mockServices.planning.getPlans.mockResolvedValue(DEMO_PLANS);
    mockServices.planning.getPlanById.mockResolvedValue(DEMO_PLANS[0]);
    mockServices.simulation.runSimulation.mockResolvedValue({
      jobId: 'JOB-SIM-1',
      status: 'COMPLETED',
      requestedAt: '2026-09-09T00:00:00Z',
      completedAt: '2026-09-09T00:00:00Z',
      progressPercent: 100,
      resultEndpoint: '/api/v1/simulations/SIM-1/result',
    });
    mockServices.simulation.getSimulationResult.mockResolvedValue(DEMO_RESULT);
  });

  it('renders scenario branches and plan selection', async () => {
    render(<SimulationWorkspace />);
    expect((await screen.findAllByText(DEMO_SCENARIOS[0].name)).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByLabelText(/Candidate plan/)).toBeDefined();
    expect(screen.getByRole('button', { name: /Run Simulation/ })).toBeDefined();
  });

  it('runs simulation inside the scenario boundary and shows backend result', async () => {
    render(<SimulationWorkspace />);
    await screen.findAllByText(DEMO_SCENARIOS[0].name);
    fireEvent.click(screen.getByRole('button', { name: /Run Simulation/ }));
    await screen.findByText('JOB-SIM-1', { exact: false });
    expect(mockServices.simulation.runSimulation).toHaveBeenCalledTimes(1);
    const request = mockServices.simulation.runSimulation.mock.calls[0][0] as {
      scenarioContext: { mode: string };
    };
    expect(request.scenarioContext.mode).toBe('SCENARIO');
    expect(await screen.findByText(/Analytical evidence only/)).toBeDefined();
  });

  it('retries polling when the first result is not ready, never fabricating', async () => {
    mockServices.simulation.getSimulationResult
      .mockResolvedValueOnce(null)
      .mockResolvedValue(DEMO_RESULT);
    render(<SimulationWorkspace />);
    await screen.findAllByText(DEMO_SCENARIOS[0].name);
    fireEvent.click(screen.getByRole('button', { name: /Run Simulation/ }));
    expect(await screen.findByText(/Analytical evidence only/, {}, { timeout: 5000 })).toBeDefined();
    expect(mockServices.simulation.getSimulationResult.mock.calls.length).toBeGreaterThanOrEqual(2);
  });

  it('shows an empty state when no plans exist', async () => {
    mockServices.planning.getPlans.mockResolvedValue([]);
    render(<SimulationWorkspace />);
    expect(await screen.findByText('No plans available')).toBeDefined();
  });
});
