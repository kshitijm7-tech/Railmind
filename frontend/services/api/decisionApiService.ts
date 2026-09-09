/** F01 — Real decision/governance API service (FastAPI). */
import { apiClient, extractItemData, extractListData } from './client/httpClient';
import { RailmindApiError } from './client/errors';
import type { IDecisionService } from '../types';
import type { DecisionRecord } from '../../domain';
import type { ApproveDecisionBody, RejectDecisionBody, DeferDecisionBody } from '../../contracts/api/decision';
import { mapDecision } from './mappers';

export class ApiDecisionService implements IDecisionService {
  async getDecisionHistory(): Promise<DecisionRecord[]> {
    const env = await apiClient.get('/decisions', { query: { page: 1, page_size: 100 } });
    return extractListData<unknown>(env, 'GET /decisions').map(mapDecision);
  }

  async approveDecision(id: string, body: ApproveDecisionBody): Promise<DecisionRecord> {
    const env = await apiClient.post(`/decisions/${encodeURIComponent(id)}/approve`, {
      approver: body.approver,
      role: body.role,
      justification: body.justification,
      comments: body.comments,
    });
    const item = extractItemData<unknown>(env, `POST /decisions/${id}/approve`);
    if (!item) throw new RailmindApiError({ kind: 'MALFORMED', message: 'Approve returned an unexpected shape.' });
    return mapDecision(item);
  }

  async rejectDecision(id: string, body: RejectDecisionBody): Promise<DecisionRecord> {
    const env = await apiClient.post(`/decisions/${encodeURIComponent(id)}/reject`, {
      approver: body.approver,
      role: body.role,
      reason: body.reason,
    });
    const item = extractItemData<unknown>(env, `POST /decisions/${id}/reject`);
    if (!item) throw new RailmindApiError({ kind: 'MALFORMED', message: 'Reject returned an unexpected shape.' });
    return mapDecision(item);
  }

  async deferDecision(id: string, body: DeferDecisionBody): Promise<DecisionRecord> {
    const env = await apiClient.post(`/decisions/${encodeURIComponent(id)}/defer`, {
      approver: body.approver,
      role: body.role,
      reason: body.reason,
      deferUntil: body.deferUntil,
    });
    const item = extractItemData<unknown>(env, `POST /decisions/${id}/defer`);
    if (!item) throw new RailmindApiError({ kind: 'MALFORMED', message: 'Defer returned an unexpected shape.' });
    return mapDecision(item);
  }

  async submitDecision(_record: Omit<DecisionRecord, 'decision_id' | 'timestamp'>): Promise<DecisionRecord> {
    // No generic submit endpoint on the backend; approve/reject/defer are
    // explicit. Kept on the interface for backward compat with existing pages.
    throw new RailmindApiError({
      kind: 'NOT_IMPLEMENTED',
      message: 'Generic decision submit has no backend endpoint (mock fallback in use).',
    });
  }
}
