import { ApiListResponse } from '../common/envelope';

// Reuses the AuditEvent from domain decisions
import type { AuditEvent } from '../../../domain/types/decisions';

export type AuditEventListResponse = ApiListResponse<AuditEvent>;
