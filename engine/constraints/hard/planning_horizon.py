"""HARD — Planning horizon containment (PRD §27.10, TRD planning config)."""

from typing import Optional

from engine.models.context import ConstraintContext
from engine.constraints.base import ConstraintRule
from engine.constraints.types import ConstraintType
from engine.constraints.severity import ConstraintSeverity
from engine.constraints._toolkit import evidence, make_result


class PlanningHorizonRule(ConstraintRule):
    """A proposed block must lie inside the configured planning horizon.

    Horizon containment is inclusive at both boundaries. If no horizon is
    supplied the rule passes with an explicit INFO note that horizon checking
    is disabled — this is configuration, not an accidental skip.
    """

    rule_id = "RAILMIND.HARD.PLANNING_HORIZON"
    rule_version = "1.0.0"
    name = "Planning horizon containment"
    description = "The block interval must be contained in the configured planning horizon (inclusive)."
    constraint_type = ConstraintType.HARD

    def evaluate(self, context: ConstraintContext):
        block = context.candidate_block
        horizon = context.planning_horizon

        if horizon is None:
            return make_result(
                self,
                "PASS",
                ConstraintSeverity.INFO,
                "Planning horizon not configured",
                "No planning horizon was supplied; horizon containment is "
                "disabled for this evaluation (explicit configuration).",
                [evidence("configuration", "planning_horizon not set")],
                [f"section:{block.section_id}"],
            )

        contained = horizon.contains(block.interval)
        ev = [
            evidence("candidate_block", "Block start offset from horizon start (minutes)",
                     (block.interval.start - horizon.start).total_seconds() / 60.0),
            evidence("candidate_block", "Horizon end minus block end (minutes)",
                     (horizon.end - block.interval.end).total_seconds() / 60.0),
        ]

        if contained:
            return make_result(
                self,
                "PASS",
                ConstraintSeverity.INFO,
                "Block inside planning horizon",
                "Block is fully contained in the planning horizon (inclusive).",
                ev,
                [f"section:{block.section_id}"],
            )

        before = max(0.0, (horizon.start - block.interval.start).total_seconds() / 60.0)
        after = max(0.0, (block.interval.end - horizon.end).total_seconds() / 60.0)
        overshoot = before + after
        ev.append(evidence("candidate_block", "Total horizon overshoot (minutes)", overshoot))
        return make_result(
            self,
            "FAIL",
            ConstraintSeverity.ERROR,
            "Block outside planning horizon",
            (
                f"Block exceeds the planning horizon by {overshoot:.1f} minutes "
                f"({before:.1f} before start, {after:.1f} after end)."
            ),
            ev,
            [f"section:{block.section_id}"],
            violation_degree=overshoot,
        )
