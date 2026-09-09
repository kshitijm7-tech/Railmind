"""HARD — Task dependency precedence (PRD §27.5, TRD §24.6, blueprint §17.4 c8)."""

from typing import Dict

from engine.models.context import ConstraintContext
from engine.constraints.base import ConstraintRule
from engine.constraints.types import ConstraintType
from engine.constraints.severity import ConstraintSeverity
from engine.constraints._toolkit import evidence, make_result


class TaskDependencyRule(ConstraintRule):
    """Assigned task dependencies must respect precedence (blueprint §17.4 c8).

    Semantics: if task T depends on task D, the block carrying D must end no
    later than the start of the block carrying T. The engine evaluates one
    candidate block at a time, so it can detect:

    - T is assigned here while D is scheduled in an existing block that ends
      after this block starts → FAIL (predecessor not finished in time);
    - D is assigned here but T is neither scheduled nor assigned → the
      dependency cannot be verified → FAIL (fail-closed);
    - both tasks assigned to this block → intra-block sequencing is accepted
      at E01 and deferred to E03's model (documented limitation).

    Known E01 limitation: scheduled-task references do not yet carry their own
    dependency metadata, so the successor direction (a scheduled successor
    starting before this block ends) cannot be detected here. Recorded in
    docs/E01_Report.md.
    """

    rule_id = "RAILMIND.HARD.TASK_DEPENDENCY_PRECEDENCE"
    rule_version = "1.0.0"
    name = "Task dependency precedence"
    description = (
        "Dependent tasks must respect precedence: the predecessor's block must "
        "finish before the successor's block starts; unresolvable dependencies "
        "fail closed."
    )
    constraint_type = ConstraintType.HARD

    def evaluate(self, context: ConstraintContext):
        block = context.candidate_block
        scheduled: Dict[str, "object"] = {t.task_id: t for t in context.scheduled_tasks}
        assigned_ids = {t.task_id for t in context.tasks}

        # Map dependency → kinds of problem found.
        failures = []  # (task_id, dependency_id, reason)

        for task in context.tasks:
            for dep_id in task.depends_on:
                if dep_id in assigned_ids:
                    continue  # same block: intra-block order is out of E01 scope
                dep = scheduled.get(dep_id)
                if dep is None:
                    failures.append(
                        (task.task_id, dep_id, "predecessor is not scheduled anywhere")
                    )
                    continue
                if dep.interval.end > block.interval.start:
                    failures.append(
                        (
                            task.task_id,
                            dep_id,
                            (
                                f"predecessor block ends at {dep.interval.end.isoformat()}, "
                                f"after this block starts at {block.interval.start.isoformat()}"
                            ),
                        )
                    )

        if not failures:
            dep_count = sum(len(t.depends_on) for t in context.tasks)
            return make_result(
                self,
                "PASS",
                ConstraintSeverity.INFO,
                "Task dependencies respected",
                (
                    f"All {dep_count} dependency relation(s) for assigned tasks "
                    "respect precedence."
                    if dep_count
                    else "Assigned tasks have no dependencies."
                ),
                [evidence("tasks", "Dependency relations checked", float(dep_count))],
                [f"section:{block.section_id}"],
            )

        failures.sort(key=lambda f: (f[0], f[1]))
        ev = [
            evidence(f"task:{task_id}", f"dependency {dep_id}: {reason}")
            for task_id, dep_id, reason in failures
        ]
        entities = sorted({f"task:{f[0]}" for f in failures} | {f"task:{f[1]}" for f in failures})
        return make_result(
            self,
            "FAIL",
            ConstraintSeverity.ERROR,
            "Task dependency precedence violated",
            "; ".join(f"{dep_id} → {task_id}: {reason}" for task_id, dep_id, reason in failures) + ".",
            ev,
            [f"section:{block.section_id}"] + entities,
        )

