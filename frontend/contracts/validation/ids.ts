import { DomainError, ERROR_CODES } from '../common/errors';
import { makeTimestamp } from '../common/ids';

export function validateId(id: string, prefix: string): DomainError | null {
  if (!id || id.trim() === '') {
    return { code: ERROR_CODES.MISSING_REQUIRED_ID, message: `ID cannot be empty for ${prefix}`, category: 'VALIDATION', severity: 'ERROR', timestamp: makeTimestamp(new Date().toISOString()) };
  }
  return null;
}
