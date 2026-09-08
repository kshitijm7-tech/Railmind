"""HARD — Corridor/section availability (PRD §27.3, TRD §24.2)."""

from engine.models.context import ConstraintContext
from engine.constraints.base import ConstraintRule
from engine.constraints.types import ConstraintType
from engine.constraints.severity import ConstraintSeverity
from engine.constraints._toolkit import evidence, find_corridor, find_section_state, make_result


class CorridorAvailabilityRule(ConstraintRule):
    """The block may only run where its section and corridor are available.

    Two independent checks on canonical relationships only:
    - the section's operational status must not be CLOSED;
    - the corridor containing the section (via ``CorridorState.section_ids``)
      must be available.

    No identifier-to-name mapping is ever hard-coded. Data gaps fail closed.
    """

    rule_id = "RAILMIND.HARD.CORRIDOR_AVAILABILITY"
    rule_version = "1.0.0"
    name = "Corridor availability"
    description = (
        "The affected section must not be CLOSED and its corridor must be "
        "available for maintenance activity."
    )
    constraint_type = ConstraintType.HARD

    def evaluate(self, context: ConstraintContext):
        block = context.candidate_block
        entity = f"section:{block.section_id}"

        state = find_section_state(context)
        if state is None:
            return make_result(
                self,
                "FAIL",
                ConstraintSeverity.ERROR,
                "Section status unknown",
                (
                    f"No infrastructure state was supplied for section "
                    f"{block.section_id}; availability cannot be verified "
                    "(fail-closed)."
                ),
                [evidence("context", "Section states supplied", float(len(context.section_states)))],
                [entity],
            )

        if state.status == "CLOSED":
            return make_result(
                self,
                "FAIL",
                ConstraintSeverity.CRITICAL,
                "Section is closed",
                f"Section {block.section_id} is CLOSED and cannot host a block.",
                [evidence(f"section:{block.section_id}", "Infrastructure status", 0.0)],
                [entity],
                violation_degree=1.0,
            )

        corridor = find_corridor(context, block.section_id)
        if corridor is None:
            return make_result(
                self,
                "FAIL",
                ConstraintSeverity.ERROR,
                "No corridor for section",
                (
                    f"Section {block.section_id} is not a member of any supplied "
                    f"corridor; corridor availability cannot be verified "
                    "(fail-closed)."
                ),
                [evidence("context", "Corridors supplied", float(len(context.corridors)))],
                [entity],
            )

        if not corridor.is_available:
            return make_result(
                self,
                "FAIL",
                ConstraintSeverity.CRITICAL,
                "Corridor unavailable",
                (
                    f"Corridor {corridor.corridor_id} containing section "
                    f"{block.section_id} is marked unavailable."
                ),
                [evidence(f"corridor:{corridor.corridor_id}", "Corridor availability", 0.0)],
                [entity, f"corridor:{corridor.corridor_id}"],
                violation_degree=1.0,
            )

        return make_result(
            self,
            "PASS",
            ConstraintSeverity.INFO,
            "Corridor and section available",
            (
                f"Section {block.section_id} is {state.status.value} and corridor "
                f"{corridor.corridor_id} is available."
            ),
            [
                evidence(f"section:{block.section_id}", f"Infrastructure status {state.status.value}"),
                evidence(f"corridor:{corridor.corridor_id}", "Corridor available"),
            ],
            [entity, f"corridor:{corridor.corridor_id}"],
        )
