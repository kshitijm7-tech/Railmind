"""HARD — Block duration validity (PRD §27.4, TRD §24.5, blueprint §17.4 c6)."""

from typing import List, Optional

from engine.models.context import ConstraintContext
from engine.constraints.base import ConstraintRule
from engine.constraints.types import ConstraintType
from engine.constraints.severity import ConstraintSeverity
from engine.constraints._toolkit import evidence, make_result, max_task_minutes


class BlockDurationRule(ConstraintRule):
    """The block interval must be positive and fit the assigned maintenance work.

    Fails when:
    - the block duration is zero or negative, or
    - a task's maximum duration estimate exceeds the block length, or
    - no task carries the block (a block must do maintenance work).
    """

    rule_id = "RAILMIND.HARD.BLOCK_DURATION"
    rule_version = "1.0.0"
    name = "Block duration validity"
    description = (
        "Block duration must be positive and must accommodate the maximum "
        "duration estimate of every assigned maintenance task."
    )
    constraint_type = ConstraintType.HARD

    def evaluate(self, context: ConstraintContext):
        block_minutes = context.candidate_block.interval.minutes
        ev = [evidence("candidate_block", "Block duration in minutes", block_minutes)]

        if block_minutes <= 0:
            return make_result(
                self,
                "FAIL",
                ConstraintSeverity.CRITICAL,
                "Block duration must be positive",
                f"Block interval duration is {block_minutes:.1f} minutes; "
                "a maintenance block must have a positive duration.",
                ev,
                [self._entity(context)],
                violation_degree=abs(block_minutes),
            )

        if not context.tasks:
            return make_result(
                self,
                "FAIL",
                ConstraintSeverity.ERROR,
                "Block carries no maintenance tasks",
                "Every block must carry at least one maintenance task; the "
                "candidate block has none.",
                ev,
                [self._entity(context)],
            )

        # Rule 6 (blueprint §17.4): end - start >= sum of task durations for the
        # sequential in-possession execution model.
        required_total = sum(t.duration.expected for t in context.tasks)
        worst = max_task_minutes(context)  # (task_id, maximum estimate) for evidence
        ev.append(evidence("tasks", "Sum of expected task durations (minutes)", required_total))
        if worst is not None:
            task_id = worst[0]
            maximum = next(t.duration.maximum for t in context.tasks if t.task_id == task_id)
            ev.append(evidence(f"task:{task_id}", "Maximum duration estimate (minutes)", float(maximum)))

        deficit = required_total - block_minutes
        if deficit > 0:
            return make_result(
                self,
                "FAIL",
                ConstraintSeverity.ERROR,
                "Block too short for assigned maintenance",
                (
                    f"Assigned maintenance needs {required_total:.1f} minutes "
                    f"(sequential execution) but the block is only "
                    f"{block_minutes:.1f} minutes long — a {deficit:.1f}-minute deficit."
                ),
                ev,
                [self._entity(context)] + [f"task:{t.task_id}" for t in context.tasks],
                violation_degree=deficit,
            )
        return make_result(
            self,
            "PASS",
            ConstraintSeverity.INFO,
            "Block duration valid",
            (
                f"Block is {block_minutes:.1f} minutes and assigned maintenance "
                f"needs {required_total:.1f} minutes — fits with "
                f"{block_minutes - required_total:.1f} minutes of slack."
            ),
            ev,
            [self._entity(context)],
        )

    @staticmethod
    def _entity(context: ConstraintContext) -> str:
        block_id = context.candidate_block.block_id
        return f"block:{block_id}" if block_id else "block:candidate"
