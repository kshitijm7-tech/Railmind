"""HARD — Task deadline (PRD §27.11, blueprint §17.4 c9, TRD §24.7)."""

from typing import Optional

from engine.models.context import ConstraintContext
from engine.constraints.base import ConstraintRule
from engine.constraints.types import ConstraintType
from engine.constraints.severity import ConstraintSeverity
from engine.constraints._toolkit import evidence, make_result


class TaskDeadlineRule(ConstraintRule):
    """A task with a mandatory ``latest_finish`` must complete by its deadline.

    Evaluated per assigned task; only tasks with a non-null deadline constrain
    the block (blueprint §11.2: deadline may be null). The binding constraint
    is the earliest deadline among assigned tasks.
    """

    rule_id = "RAILMIND.HARD.TASK_DEADLINE"
    rule_version = "1.0.0"
    name = "Task deadline"
    description = (
        "Any assigned task with a mandatory latest_finish deadline must finish "
        "no later than that deadline."
    )
    constraint_type = ConstraintType.HARD

    def evaluate(self, context: ConstraintContext):
        block = context.candidate_block
        constrained = [t for t in context.tasks if t.latest_finish is not None]

        if not constrained:
            return make_result(
                self,
                "PASS",
                ConstraintSeverity.INFO,
                "No constrained tasks",
                "No assigned task carries a mandatory deadline.",
                [evidence("tasks", "Assigned tasks with deadlines", float(len(constrained)))],
                [f"section:{block.section_id}"],
            )

        binding = min(constrained, key=lambda t: (t.latest_finish, t.task_id))
        ev = [
            evidence(f"task:{binding.task_id}", "Earliest mandatory deadline", 0.0),
            evidence("candidate_block", "Block end minus deadline (minutes)",
                     (binding.latest_finish - block.interval.end).total_seconds() / 60.0),
        ]

        if block.interval.end <= binding.latest_finish:
            slack = (binding.latest_finish - block.interval.end).total_seconds() / 60.0
            return make_result(
                self,
                "PASS",
                ConstraintSeverity.INFO,
                "All task deadlines met",
                (
                    f"Block ends {slack:.1f} minutes before the earliest "
                    f"mandatory deadline (task {binding.task_id})."
                ),
                ev,
                [f"section:{block.section_id}"] + [f"task:{t.task_id}" for t in constrained],
            )

        lateness = (block.interval.end - binding.latest_finish).total_seconds() / 60.0
        return make_result(
            self,
            "FAIL",
            ConstraintSeverity.ERROR,
            "Task deadline missed",
            (
                f"Block ends {lateness:.1f} minutes after the mandatory deadline "
                f"of task {binding.task_id}."
            ),
            ev,
            [f"section:{block.section_id}"] + [f"task:{t.task_id}" for t in constrained],
            violation_degree=lateness,
        )
