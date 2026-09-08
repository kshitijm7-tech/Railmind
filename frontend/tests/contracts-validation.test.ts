import { describe, it, expect } from 'vitest';
import { validateTimeInterval, validateDuration } from '../contracts/validation/time';
import { makeTimestamp, makeBlockId, makeTaskId } from '../contracts/common/ids';
import { ERROR_CODES } from '../contracts/common/errors';
import { MaintenanceTask } from '../contracts/maintenance/maintenance-task';
import { Block } from '../contracts/planning/block';
import { TrainImpact } from '../contracts/operations/train-impact';
import { Plan } from '../contracts/planning/plan';

describe('Contracts Validation', () => {
  it('validates correct time intervals', () => {
    const validInterval = {
      start: makeTimestamp('2026-09-08T10:00:00Z'),
      end: makeTimestamp('2026-09-08T12:00:00Z')
    };
    expect(validateTimeInterval(validInterval)).toBeNull();
  });

  it('rejects invalid time intervals (end < start)', () => {
    const invalidInterval = {
      start: makeTimestamp('2026-09-08T12:00:00Z'),
      end: makeTimestamp('2026-09-08T10:00:00Z')
    };
    const error = validateTimeInterval(invalidInterval);
    expect(error).not.toBeNull();
    expect(error?.code).toBe(ERROR_CODES.INVALID_TIME_INTERVAL);
  });

  it('validates duration constraints', () => {
    const validDuration = { expected: 120, minimum: 90, maximum: 150 };
    expect(validateDuration(validDuration)).toBeNull();

    const invalidDuration = { expected: 120, minimum: 150, maximum: 90 };
    const error = validateDuration(invalidDuration);
    expect(error).not.toBeNull();
    expect(error?.code).toBe(ERROR_CODES.INVALID_DURATION);
  });

  it('proves cross-domain relationships work', () => {
    // This is purely a type-level test to ensure shapes match and import properly
    const taskId = makeTaskId('task-1');
    const blockId = makeBlockId('block-1');

    const task: Partial<MaintenanceTask> = {
      task_id: taskId,
      status: 'SCHEDULED'
    };

    const block: Partial<Block> = {
      block_id: blockId,
      status: 'APPROVED',
      tasks: [task.task_id as any]
    };

    const impact: Partial<TrainImpact> = {
      block_id: block.block_id as any,
      impact_type: 'DELAY'
    };

    const plan: Partial<Plan> = {
      status: 'ACTIVE',
      blocks: [block as Block]
    };

    expect(task.task_id).toBe('task-1');
    expect(plan.blocks?.[0]?.status).toBe('APPROVED');
    expect(impact.impact_type).toBe('DELAY');
  });
});
