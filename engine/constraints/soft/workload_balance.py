"""SOFT — Workload balance across sections (TRD §20)."""

from engine.models.context import ConstraintContext
from engine.constraints.base import ConstraintRule
from engine.constraints.types import ConstraintType
from engine.constraints.severity import ConstraintSeverity
from engine.constraints._toolkit import evidence, make_result


def _deviation_percent(value: float, reference: float) -> float:
    if reference <= 0:
        return 0.0
    return abs(value - reference) / reference * 100.0


class WorkloadBalanceRule(ConstraintRule):
    """Maintenance load should spread evenly across sections in the context.

    SOFT: compares the candidate block's per-section maintenance minutes
    (assigned task durations) with the average load per section derived from
    the supplied scheduled tasks. Warnings only; never affects feasibility.
    """

    rule_id = "RAILMIND.SOFT.WORKLOAD_BALANCE"
    rule_version = "1.0.0"
    name = "Workload balancing"
    description = (
        "The candidate section's maintenance load should stay within the "
        "configured tolerance of the average per-section load."
    )
    constraint_type = ConstraintType.SOFT

    def evaluate(self, context: ConstraintContext):
        block = context.candidate_block
        section_id = block.section_id
        tolerance = context.configuration.workload_balance_tolerance_percent

        # Existing load per section from scheduled task layout.
        load: dict = {}
        for scheduled in context.scheduled_tasks:
            load[scheduled.section_id] = load.get(scheduled.section_id, 0.0)
        for task in context.tasks:
            load[section_id] = load.get(section_id, 0.0) + task.duration.expected

        # ScheduledTaskRef does not carry durations; occupancy records provide
        # the proxy load for other sections (their exclusive-use minutes).
        for occupancy in context.section_occupancies:
            minutes = occupancy.interval.minutes
            load[occupancy.section_id] = load.get(occupancy.section_id, 0.0) + minutes

        if not load:
            return make_result(
                self,
                "PASS",
                ConstraintSeverity.INFO,
                "No workload data",
                "No maintenance workload information supplied; balancing not assessable.",
                [evidence("context", "Scheduled sections", 0.0)],
                [f"section:{section_id}"],
            )

        average = sum(load.values()) / len(load)
        mine = load.get(section_id, 0.0)
        deviation = _deviation_percent(mine, average)
        ev = [
            evidence("context", f"Candidate section load (minutes)", mine),
            evidence("context", f"Average per-section load (minutes)", average),
            evidence("context", f"Deviation (percent of average)", deviation),
        ]

        if deviation <= tolerance:
            return make_result(
                self,
                "PASS",
                ConstraintSeverity.INFO,
                "Workload balanced",
                (
                    f"Section {section_id} carries {mine:.1f} maintenance minutes "
                    f"vs {average:.1f} average — within the {tolerance:.0f}% tolerance."
                ),
                ev,
                [f"section:{section_id}"],
            )

        return make_result(
            self,
            "WARNING",
            ConstraintSeverity.WARNING,
            "Workload imbalance",
            (
                f"Section {section_id} carries {mine:.1f} maintenance minutes vs "
                f"{average:.1f} average — {deviation:.0f}% deviation exceeds the "
                f"{tolerance:.0f}% tolerance."
            ),
            ev,
            [f"section:{section_id}"],
            violation_degree=deviation - tolerance,
        )
