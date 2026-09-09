/** F01 — Real planning API service (FastAPI). */
import { apiClient, extractItemData, extractListData } from './client/httpClient';
import type { IPlanningService } from '../types';
import type { CandidateBlockWindow, Plan } from '../../domain';
import type { BlockListQuery, ComparePlansRequest, GeneratePlanRequest, PlanListQuery } from '../../contracts/api/planning';
import type { AsyncJob } from '../../contracts/api/common/job';
import { mapAsyncJob, mapCandidateWindow, mapPlan } from './mappers';

export class ApiPlanningService implements IPlanningService {
  async getCandidateWindows(_query?: BlockListQuery): Promise<CandidateBlockWindow[]> {
    // Backend stub returns an empty list today (documented gap); the mock
    // fallback in auto mode still provides demo windows for F02+.
    const env = await apiClient.get('/planning/candidates');
    const items = extractListData<unknown>(env, 'GET /planning/candidates');
    return items.map((item, index) => mapCandidateWindow(item, index));
  }

  async getPlans(query?: PlanListQuery): Promise<Plan[]> {
    const env = await apiClient.get('/plans', {
      query: { page: query?.page ?? 1, page_size: Math.min(query?.pageSize ?? 50, 100) },
    });
    return extractListData<unknown>(env, 'GET /plans').map(mapPlan);
  }

  async getPlanById(id: string): Promise<Plan | null> {
    const env = await apiClient.get(`/plans/${encodeURIComponent(id)}`);
    const item = extractItemData<unknown>(env, `GET /plans/${id}`);
    if (!item) return null;
    return mapPlan(item);
  }

  async generatePlan(request: GeneratePlanRequest): Promise<AsyncJob> {
    // Backend returns 202 + AsyncJob with resultEndpoint -> /api/v1/plans/{id}.
    const wire = await apiClient.post('/planning/generate', request);
    return mapAsyncJob(wire);
  }

  async comparePlans(request: ComparePlansRequest): Promise<Plan[]> {
    const response = (await apiClient.post('/plans/compare', {
      planIds: request.planIds,
      scenarioContext: request.scenarioContext,
    })) as { candidates?: Array<{ planId?: string }> };
    const ids = Array.isArray(response?.candidates)
      ? response.candidates.map((c) => String(c?.planId ?? '')).filter(Boolean)
      : [];
    const plans: Plan[] = [];
    for (const id of ids) {
      const plan = await this.getPlanById(id);
      if (plan) plans.push(plan);
    }
    return plans;
  }
}
