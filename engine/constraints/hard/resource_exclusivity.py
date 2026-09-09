"""HARD — Resource exclusivity & crew capacity (PRD §27.6/27.7, TRD §24.3/24.4).

Resource identity follows the canonical vocabulary: crew pools are organised
per department (blueprint §11.5) and tasks declare their department. The rule
never invents railway resource semantics beyond what the context supplies.
"""

from typing import Dict, List

from engine.models.context import ConstraintContext
from engine.constraints.base import ConstraintRule
from engine.constraints.types import ConstraintType
from engine.constraints.severity import ConstraintSeverity
from engine.constraints._toolkit import evidence, make_result, overlap_minutes


class ResourceExclusivityRule(ConstraintRule):
    """Exclusive resources must not be double-booked; pool capacity must hold.

    Two mechanisms, both deterministic:
    1. Pool capacity: for each department pool covering the block interval,
       total required crew units (claimed tasks + overlapping existing
       demands) must not exceed ``units_available``.
    2. Explicit exclusivity: a pool flagged ``is_exclusive`` may host only one
       allocation in the interval (claimed pool + any overlapping demand).
    """

    rule_id = "RAILMIND.HARD.RESOURCE_EXCLUSIVITY"
    rule_version = "1.0.0"
    name = "Resource exclusivity and capacity"
    description = (
        "Required crew units must fit within department pool capacity for the "
        "block interval, and pools flagged exclusive must not be double-booked."
    )
    constraint_type = ConstraintType.HARD

    def evaluate(self, context: ConstraintContext):
        block = context.candidate_block
        claimed_pool_ids = set(block.resource_pool_ids)
        required: Dict[str, int] = {}
        for task in context.tasks:
            if task.crew_units_required > 0:
                required[task.department] = required.get(task.department, 0) + task.crew_units_required

        ev: List = []

        # --- Capacity per department pool -------------------------------
        # Only departments whose tasks actually require crew units demand a
        # pool (zero-crew tasks impose no staffing constraint).
        for pool in context.resource_pools:
            if required.get(pool.department, 0) <= 0:
                continue
            needed_now = required[pool.department]
            pool_covers_block = pool.availability is None or pool.availability.overlaps(block.interval)
            if not pool_covers_block:
                ev.append(
                    evidence(
                        f"pool:{pool.pool_id}",
                        f"Pool shift window does not cover the block interval; "
                        f"{needed_now} units of {pool.department} work cannot be staffed",
                    )
                )
                return make_result(
                    self,
                    "FAIL",
                    ConstraintSeverity.ERROR,
                    "Resource pool unavailable in block interval",
                    (
                        f"Pool {pool.pool_id} ({pool.department}) does not cover "
                        f"the block interval; {needed_now} unit(s) required cannot be staffed."
                    ),
                    ev,
                    [f"pool:{pool.pool_id}", f"section:{block.section_id}"],
                )
            overlapping = [
                d
                for d in context.resource_demands
                if d.pool_id == pool.pool_id and overlap_minutes(
                    block.interval.start, block.interval.end, d.interval.start, d.interval.end
                ) > 0
            ]
            used = sum(d.units for d in overlapping)
            ev.append(
                evidence(
                    f"pool:{pool.pool_id}",
                    f"{pool.department} pool: required {needed_now} + committed {used} "
                    f"of {pool.units_available} available",
                    float(needed_now + used),
                )
            )
            if needed_now + used > pool.units_available:
                deficit = needed_now + used - pool.units_available
                return make_result(
                    self,
                    "FAIL",
                    ConstraintSeverity.ERROR,
                    "Resource pool capacity exceeded",
                    (
                        f"Pool {pool.pool_id} ({pool.department}) needs {needed_now} "
                        f"unit(s) for the block plus {used} already committed, but only "
                        f"{pool.units_available} are available — short by {deficit}."
                    ),
                    ev,
                    [f"pool:{pool.pool_id}", f"section:{block.section_id}"],
                    violation_degree=float(deficit),
                )

        # Departments with required crew but no pool record: fail closed —
        # staffing cannot be verified.
        known_departments = {p.department for p in context.resource_pools}
        unstaffed = sorted(set(required) - known_departments)
        if unstaffed:
            return make_result(
                self,
                "FAIL",
                ConstraintSeverity.ERROR,
                "No resource pool for required department",
                (
                    f"Tasks require crew for department(s) {', '.join(unstaffed)} "
                    "but no matching resource pool was supplied; staffing cannot "
                    "be verified (fail-closed)."
                ),
                ev,
                [f"section:{block.section_id}"] + [f"department:{d}" for d in unstaffed],
            )

        # --- Explicitly exclusive pools ----------------------------------
        for pool in context.resource_pools:
            if not pool.is_exclusive:
                continue
            claimed = pool.pool_id in claimed_pool_ids
            clashing = [
                d
                for d in context.resource_demands
                if d.pool_id == pool.pool_id and overlap_minutes(
                    block.interval.start, block.interval.end, d.interval.start, d.interval.end
                ) > 0
            ]
            if claimed and clashing:
                ids = ", ".join(sorted(d.demand_id for d in clashing))
                return make_result(
                    self,
                    "FAIL",
                    ConstraintSeverity.ERROR,
                    "Exclusive resource double-booked",
                    (
                        f"Exclusive pool {pool.pool_id} is claimed by this block "
                        f"and already has overlapping demand(s): {ids}."
                    ),
                    ev,
                    [f"pool:{pool.pool_id}"] + [f"demand:{d.demand_id}" for d in clashing],
                )

        return make_result(
            self,
            "PASS",
            ConstraintSeverity.INFO,
            "Resources available",
            (
                "Required crew fits within pool capacity and no exclusive "
                "resource is double-booked."
            ),
            ev,
            [f"section:{block.section_id}"],
        )
