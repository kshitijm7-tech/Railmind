"""HARD — Train-path conflicts (PRD §27.9, TRD §24.8, blueprint §17.4)."""

from typing import List

from engine.models.context import ConstraintContext
from engine.constraints.base import ConstraintRule
from engine.constraints.types import ConstraintType
from engine.constraints.severity import ConstraintSeverity
from engine.constraints._toolkit import evidence, make_result, overlap_minutes


class TrainConflictRule(ConstraintRule):
    """A maintenance block must not overlap any scheduled train path on its section.

    Overlap is strict: a train path ending exactly when the block starts (and
    vice versa) is NOT a conflict — adjacent occupancy of the section is legal
    because the section is handed over at the boundary instant. The rule checks
    only the block's own section; a train segment on a different section never
    conflicts with this block (per-section exclusivity is expressed by
    RAILMIND.HARD.SECTION_EXCLUSIVITY / TRACK_OCCUPANCY rules).
    """

    rule_id = "RAILMIND.HARD.TRAIN_PATH_CONFLICT"
    rule_version = "1.0.0"
    name = "Train-path conflict"
    description = (
        "The block interval must not overlap any scheduled train-path segment "
        "on the block's section (strict overlap; adjacent is allowed)."
    )
    constraint_type = ConstraintType.HARD

    def evaluate(self, context: ConstraintContext):
        block = context.candidate_block
        section_id = block.section_id
        conflicts = []  # (train_id, minutes, segment_start, segment_end)

        for path in context.train_paths:
            for segment in path.segments:
                if segment.section_id != section_id:
                    continue
                minutes = overlap_minutes(
                    block.interval.start,
                    block.interval.end,
                    segment.interval.start,
                    segment.interval.end,
                )
                if minutes > 0:
                    conflicts.append((path.train_id, minutes, segment.interval.start, segment.interval.end))

        # Deterministic ordering for stable evidence.
        conflicts.sort(key=lambda c: (c[0], c[2]))

        if not conflicts:
            checked = sum(
                1
                for path in context.train_paths
                for segment in path.segments
                if segment.section_id == section_id
            )
            return make_result(
                self,
                "PASS",
                ConstraintSeverity.INFO,
                "No train-path conflict",
                (
                    f"Block does not overlap any of the {checked} scheduled "
                    f"train-path segments on section {section_id}."
                ),
                [evidence("context", "Train segments on block section", float(checked))],
                [f"section:{section_id}"],
            )

        total = sum(c[1] for c in conflicts)
        ev: List = [
            evidence(
                f"train:{train_id}",
                (
                    f"Overlaps block by {minutes:.1f} min "
                    f"(segment {start.isoformat()} → {end.isoformat()})"
                ),
                minutes,
            )
            for train_id, minutes, start, end in conflicts
        ]
        ev.append(evidence("candidate_block", "Total conflicting overlap (minutes)", total))
        return make_result(
            self,
            "FAIL",
            ConstraintSeverity.CRITICAL,
            "Block conflicts with scheduled train path",
            (
                f"Block overlaps {len(conflicts)} train-path segment(s) on "
                f"section {section_id} for a total of {total:.1f} minutes: "
                + ", ".join(sorted({c[0] for c in conflicts}))
                + "."
            ),
            ev,
            [f"section:{section_id}"] + [f"train:{c[0]}" for c in conflicts],
            violation_degree=total,
        )
