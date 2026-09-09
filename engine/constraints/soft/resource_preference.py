"""SOFT — Preferred resource allocation (TRD §20)."""

from engine.models.context import ConstraintContext
from engine.constraints.base import ConstraintRule
from engine.constraints.types import ConstraintType
from engine.constraints.severity import ConstraintSeverity
from engine.constraints._toolkit import evidence, make_result


class ResourcePreferenceRule(ConstraintRule):
    """Blocks should use their department's own resource pools.

    SOFT: when a task's department has no dedicated pool record, the block
    relies on shared/unspecified resourcing — warn, never fail. If every
    required department has a pool, PASS.
    """

    rule_id = "RAILMIND.SOFT.RESOURCE_PREFERENCE"
    rule_version = "1.0.0"
    name = "Preferred resource allocation"
    description = (
        "Assigned tasks should be served by dedicated department resource "
        "pools; missing pool mapping produces a warning."
    )
    constraint_type = ConstraintType.SOFT

    def evaluate(self, context: ConstraintContext):
        block = context.candidate_block
        required = sorted({t.department for t in context.tasks})
        pool_departments = {p.department for p in context.resource_pools}
        unmapped = [d for d in required if d not in pool_departments]

        ev = [
            evidence("tasks", "Departments required", float(len(required))),
            evidence("context", "Departments with dedicated pools", float(len(pool_departments))),
        ]
        entities = [f"section:{block.section_id}"]

        if not required:
            return make_result(
                self,
                "PASS",
                ConstraintSeverity.INFO,
                "No resource requirements",
                "The block carries no tasks; resource preference not assessable.",
                ev,
                entities,
            )

        if unmapped:
            ev.append(
                evidence("tasks", f"Departments without dedicated pool: {', '.join(unmapped)}")
            )
            return make_result(
                self,
                "WARNING",
                ConstraintSeverity.WARNING,
                "Tasks rely on unmapped resources",
                (
                    f"Department(s) {', '.join(unmapped)} have no dedicated "
                    "resource pool; the block would rely on unspecified resourcing."
                ),
                ev,
                entities + [f"department:{d}" for d in unmapped],
            )

        return make_result(
            self,
            "PASS",
            ConstraintSeverity.INFO,
            "Dedicated resources available",
            (
                f"All {len(required)} required department(s) have dedicated "
                "resource pools."
            ),
            ev,
            entities,
        )
