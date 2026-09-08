"""SOFT — Preferred maintenance window (TRD §20, E01 §17)."""

from datetime import timedelta

from engine.models.context import ConstraintContext
from engine.constraints.base import ConstraintRule
from engine.constraints.types import ConstraintType
from engine.constraints.severity import ConstraintSeverity
from engine.constraints._toolkit import evidence, make_result


def _minutes_outside_preferred(start_hour: int, end_hour: int, start, end) -> float:
    """Minutes of [start, end) lying outside the preferred hour window.

    The preferred window is expressed in local wall-clock hours and may wrap
    midnight (e.g. 22:00–06:00). Boundary hours are: hour h is inside iff it
    falls in the half-open span [start_hour, end_hour) mod 24 when
    start_hour < end_hour, else the wrapped union.
    """
    total_outside = 0.0
    cursor = start
    while cursor < end:
        next_boundary = min(end, cursor.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
        hour = cursor.hour
        if start_hour <= end_hour:
            inside = start_hour <= hour < end_hour
        else:  # window wraps midnight, e.g. 22:00–06:00
            inside = hour >= start_hour or hour < end_hour
        if not inside:
            total_outside += (next_boundary - cursor).total_seconds() / 60.0
        cursor = next_boundary
    return total_outside


class PreferredWindowRule(ConstraintRule):
    """Blocks should sit inside the preferred (night) maintenance window.

    SOFT: never affects feasibility; produces WARNING with the exact number of
    minutes outside the preferred window when the block deviates.
    """

    rule_id = "RAILMIND.SOFT.PREFERRED_WINDOW"
    rule_version = "1.0.0"
    name = "Preferred maintenance window"
    description = (
        "Blocks should preferably be placed inside the preferred maintenance "
        "window hours (configurable; default night possession pattern)."
    )
    constraint_type = ConstraintType.SOFT

    def evaluate(self, context: ConstraintContext):
        block = context.candidate_block
        cfg = context.configuration
        start_hour = cfg.preferred_window_start_hour
        end_hour = cfg.preferred_window_end_hour

        outside = _minutes_outside_preferred(
            start_hour, end_hour, block.interval.start, block.interval.end
        )
        ev = [
            evidence(
                "configuration",
                f"Preferred window hours {start_hour:02d}:00–{end_hour:02d}:00",
            ),
            evidence("candidate_block", "Minutes outside preferred window", outside),
        ]
        entities = [f"section:{block.section_id}"]

        if outside <= 0.0:
            return make_result(
                self,
                "PASS",
                ConstraintSeverity.INFO,
                "Block inside preferred window",
                f"Block lies entirely within the preferred maintenance window "
                f"({start_hour:02d}:00–{end_hour:02d}:00).",
                ev,
                entities,
            )

        block_minutes = block.interval.minutes
        return make_result(
            self,
            "WARNING",
            ConstraintSeverity.WARNING,
            "Block outside preferred maintenance window",
            (
                f"{outside:.1f} of {block_minutes:.1f} block minutes lie outside "
                f"the preferred maintenance window "
                f"({start_hour:02d}:00–{end_hour:02d}:00)."
            ),
            ev,
            entities,
            violation_degree=outside,
        )
