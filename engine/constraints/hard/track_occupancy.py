"""HARD — Track occupancy / section exclusivity (PRD §27.8, TRD §24.2)."""

from engine.models.context import ConstraintContext
from engine.constraints.base import ConstraintRule
from engine.constraints.types import ConstraintType
from engine.constraints.severity import ConstraintSeverity
from engine.constraints._toolkit import evidence, make_result, overlap_minutes


class TrackOccupancyRule(ConstraintRule):
    """A section cannot host overlapping blocks or other exclusive occupancy.

    The candidate block must not overlap any existing occupancy of the same
    section. Different sections never conflict merely because their timestamps
    overlap — exclusivity is per section (canonical identifiers, never names).
    Adjacent occupancies (touching endpoints) are allowed.
    """

    rule_id = "RAILMIND.HARD.SECTION_EXCLUSIVITY"
    rule_version = "1.0.0"
    name = "Track occupancy / section exclusivity"
    description = (
        "The block interval must not overlap an existing exclusive occupancy "
        "of the same section (strict overlap; adjacent is allowed)."
    )
    constraint_type = ConstraintType.HARD

    def evaluate(self, context: ConstraintContext):
        block = context.candidate_block
        section_id = block.section_id
        overlaps = []  # (occupancy_id, kind, minutes)

        for occupancy in context.section_occupancies:
            if occupancy.section_id != section_id:
                continue
            minutes = overlap_minutes(
                block.interval.start,
                block.interval.end,
                occupancy.interval.start,
                occupancy.interval.end,
            )
            if minutes > 0:
                overlaps.append((occupancy.occupancy_id, occupancy.kind, minutes))

        overlaps.sort(key=lambda o: o[0])

        if not overlaps:
            checked = sum(1 for o in context.section_occupancies if o.section_id == section_id)
            return make_result(
                self,
                "PASS",
                ConstraintSeverity.INFO,
                "Section free for the proposed interval",
                (
                    f"No existing occupancy conflicts on section {section_id} "
                    f"({checked} occupancy record(s) for this section checked)."
                ),
                [evidence("context", "Occupancy records on block section", float(checked))],
                [f"section:{section_id}"],
            )

        total = sum(o[2] for o in overlaps)
        ev = [
            evidence(
                f"occupancy:{oid}",
                f"{kind} overlaps block by {minutes:.1f} min",
                minutes,
            )
            for oid, kind, minutes in overlaps
        ]
        ev.append(evidence("candidate_block", "Total conflicting occupancy (minutes)", total))
        return make_result(
            self,
            "FAIL",
            ConstraintSeverity.CRITICAL,
            "Section already occupied",
            (
                f"Section {section_id} is already exclusively occupied during "
                f"the proposed interval by {len(overlaps)} occupancy record(s) "
                f"totalling {total:.1f} minutes of overlap."
            ),
            ev,
            [f"section:{section_id}"] + [f"occupancy:{o[0]}" for o in overlaps],
            violation_degree=total,
        )
