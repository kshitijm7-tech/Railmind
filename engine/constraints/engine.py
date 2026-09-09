"""Constraint Engine — aggregation of rules over a context.

``ConstraintEngine`` evaluates a composable list of ``ConstraintRule``s
against a ``ConstraintContext`` and aggregates the results into a
``ConstraintEvaluation`` whose ``feasible`` flag answers the E01 question:

    "Is this proposed maintenance/block plan operationally feasible?"

Feasibility semantics: feasible ⟺ no HARD rule returned FAIL. SOFT results
(PASS/WARNING) never affect feasibility.
"""

from typing import Dict, Iterable, List, Optional

from engine.constraints.base import ConstraintRule
from engine.constraints.hard import (
    BlockDurationRule,
    CorridorAvailabilityRule,
    OperationalWindowRule,
    PlanningHorizonRule,
    ResourceExclusivityRule,
    TaskDeadlineRule,
    TaskDependencyRule,
    TrackOccupancyRule,
    TrainConflictRule,
)
from engine.constraints.soft import (
    PreferredWindowRule,
    ResourcePreferenceRule,
    TrainImpactRule,
    WorkloadBalanceRule,
)
from engine.constraints.result import ConstraintEvaluation, EngineError
from engine.models.context import ConstraintContext


def default_rules() -> List[ConstraintRule]:
    """The E01 authoritative constraint set, in evaluation order.

    Hard rules first (documented order: duration → window → conflicts →
    occupancy → resources → corridor → horizon → deadline → dependency), then
    soft rules. Order does not affect feasibility, but it makes traces stable
    and readable.
    """
    return [
        # Hard (E01 §9 + PRD §27 additions)
        BlockDurationRule(),
        OperationalWindowRule(),
        TrainConflictRule(),
        TrackOccupancyRule(),
        ResourceExclusivityRule(),
        CorridorAvailabilityRule(),
        PlanningHorizonRule(),
        TaskDeadlineRule(),
        TaskDependencyRule(),
        # Soft (TRD §20)
        PreferredWindowRule(),
        TrainImpactRule(),
        WorkloadBalanceRule(),
        ResourcePreferenceRule(),
    ]


class ConstraintEngine:
    """Evaluates a fixed, ordered rule set against contexts.

    Deterministic: no clocks, no randomness, no I/O. The same context and
    configuration always produce the same evaluation.
    """

    def __init__(self, rules: Optional[Iterable[ConstraintRule]] = None):
        if rules is None:
            rules = default_rules()
        self._rules: List[ConstraintRule] = list(rules)
        self._index: Dict[str, ConstraintRule] = {}
        for rule in self._rules:
            if rule.rule_id in self._index:
                raise EngineError(f"duplicate rule_id in rule set: {rule.rule_id}")
            self._index[rule.rule_id] = rule

    @property
    def rules(self) -> List[ConstraintRule]:
        return list(self._rules)

    @property
    def rule_ids(self) -> List[str]:
        return [r.rule_id for r in self._rules]

    def rule_by_id(self, rule_id: str) -> Optional[ConstraintRule]:
        return self._index.get(rule_id)

    def evaluate(self, context: ConstraintContext) -> ConstraintEvaluation:
        """Evaluate every rule against the context and aggregate."""
        results = []
        for rule in self._rules:
            result = rule.evaluate(context)
            if result.rule_id != rule.rule_id:
                # Defensive: rules must report under their own identity.
                raise EngineError(
                    f"rule {rule.rule_id} produced a result stamped {result.rule_id}"
                )
            results.append(result)
        return ConstraintEvaluation(results=results)

    def evaluate_feasible(self, context: ConstraintContext) -> bool:
        """Convenience: feasibility verdict only."""
        return self.evaluate(context).feasible
