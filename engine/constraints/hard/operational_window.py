"""HARD — Operational window containment (PRD §27.10, TRD §24.9, blueprint §17.4 c7)."""

from engine.models.context import ConstraintContext
from engine.constraints.base import ConstraintRule
from engine.constraints.types import ConstraintType
from engine.constraints.severity import ConstraintSeverity
from engine.constraints._toolkit import evidence, find_window, make_result


class OperationalWindowRule(ConstraintRule):
    """The proposed block must be fully contained in its section's operational window.

    Containment is inclusive at the boundaries (a block starting exactly at the
    window start is contained). If no operational window is supplied for the
    block's section, the rule fails closed — possession without a valid
    operational window cannot be verified.
    """

    rule_id = "RAILMIND.HARD.OPERATIONAL_WINDOW_CONTAINMENT"
    rule_version = "1.0.0"
    name = "Operational window containment"
    description = (
        "The block must start and end within the operational window declared "
        "for its section (inclusive boundaries)."
    )
    constraint_type = ConstraintType.HARD

    def evaluate(self, context: ConstraintContext):
        block = context.candidate_block
        entity = f"section:{block.section_id}"
        window = find_window(context, )

        if window is None:
            return make_result(
                self,
                "FAIL",
                ConstraintSeverity.ERROR,
                "No operational window for section",
                (
                    f"No operational window was supplied for section "
                    f"{block.section_id}; block containment cannot be verified, "
                    "so the candidate is treated as infeasible (fail-closed)."
                ),
                [evidence("context", "Operational windows supplied", float(len(context.operational_windows)))],
                [entity],
            )

        ev = [
            evidence(f"window:{window.window_id}", "Window start"),
            evidence("candidate_block", "Block start offset from window start (minutes)",
                     (block.interval.start - window.interval.start).total_seconds() / 60.0),
            evidence("candidate_block", "Window end minus block end (minutes)",
                     (window.interval.end - block.interval.end).total_seconds() / 60.0),
        ]
        contained = window.interval.contains(block.interval)

        if contained:
            return make_result(
                self,
                "PASS",
                ConstraintSeverity.INFO,
                "Block inside operational window",
                (
                    f"Block is fully contained in operational window "
                    f"{window.window_id} (inclusive boundaries)."
                ),
                ev,
                [entity, f"window:{window.window_id}"],
            )

        overshoot_start = max(0.0, (window.interval.start - block.interval.start).total_seconds() / 60.0)
        overshoot_end = max(0.0, (block.interval.end - window.interval.end).total_seconds() / 60.0)
        degree = overshoot_start + overshoot_end
        ev.append(evidence("candidate_block", "Total boundary overshoot (minutes)", degree))
        return make_result(
            self,
            "FAIL",
            ConstraintSeverity.ERROR,
            "Block outside operational window",
            (
                f"Block is not contained in operational window {window.window_id}: "
                f"overshoot {overshoot_start:.1f} min at start, "
                f"{overshoot_end:.1f} min at end."
            ),
            ev,
            [entity, f"window:{window.window_id}"],
            violation_degree=degree,
        )
