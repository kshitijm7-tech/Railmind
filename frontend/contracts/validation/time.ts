import { TimeInterval, DurationMinutes } from '../common/time';
import { DomainError, ERROR_CODES } from '../common/errors';
import { makeTimestamp } from '../common/ids';

export function validateTimeInterval(interval: TimeInterval): DomainError | null {
  const startMs = new Date(interval.start).getTime();
  const endMs = new Date(interval.end).getTime();
  if (isNaN(startMs) || isNaN(endMs)) {
    return { code: ERROR_CODES.INVALID_TIME_INTERVAL, message: 'Invalid timestamp', category: 'VALIDATION', severity: 'ERROR', timestamp: makeTimestamp(new Date().toISOString()) };
  }
  if (startMs >= endMs) {
    return { code: ERROR_CODES.INVALID_TIME_INTERVAL, message: 'start must be before end', category: 'VALIDATION', severity: 'ERROR', timestamp: makeTimestamp(new Date().toISOString()) };
  }
  return null;
}

export function validateDuration(duration: DurationMinutes): DomainError | null {
  if (duration.expected <= 0 || duration.minimum <= 0) {
    return { code: ERROR_CODES.INVALID_DURATION, message: 'Duration must be positive', category: 'VALIDATION', severity: 'ERROR', timestamp: makeTimestamp(new Date().toISOString()) };
  }
  if (duration.minimum > duration.maximum) {
    return { code: ERROR_CODES.INVALID_DURATION, message: 'minimum must be <= maximum', category: 'VALIDATION', severity: 'ERROR', timestamp: makeTimestamp(new Date().toISOString()) };
  }
  return null;
}
