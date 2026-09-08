import { describe, it, expect } from 'vitest';
import { services } from '../services';

describe('Mock Service Layer & Deterministic Fixtures', () => {
  it('returns 6 stations and 9 track sections for Corridor C-07', async () => {
    const network = await services.network.getNetwork();
    expect(network.stations.length).toBe(6);
    expect(network.sections.length).toBe(9);
  });

  it('returns prioritized maintenance tasks', async () => {
    const tasks = await services.maintenance.getTasks();
    expect(tasks.length).toBeGreaterThan(0);
    const criticalTask = tasks.find(t => t.criticality === 'CRITICAL');
    expect(criticalTask).toBeDefined();
    expect(criticalTask?.priority_score).toBeGreaterThan(90);
  });

  it('returns train services with routes', async () => {
    const trains = await services.trains.getTrains();
    expect(trains.length).toBeGreaterThan(0);
    expect(trains[0].schedule.length).toBeGreaterThan(0);
  });

  it('performs query search across entities', async () => {
    const searchRes = await services.search.search('Shatabdi');
    expect(searchRes.length).toBe(1);
    expect(searchRes[0].category).toBe('TRAIN');
  });

  it('records decision submissions into history', async () => {
    const submission = await services.decisions.submitDecision({
      recommendation_id: 'REC-TEST-01',
      plan_id: 'PLAN-TEST-01',
      state_version: 'v1024',
      action: 'APPROVE',
      authorized_by: 'Test Controller',
      user_role: 'Operations Controller'
    });

    expect(submission.decision_id).toBeDefined();
    const history = await services.decisions.getDecisionHistory();
    expect(history.some(d => d.recommendation_id === 'REC-TEST-01')).toBe(true);
  });
});
