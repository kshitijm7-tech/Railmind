"""Constraint rule interface.

Every rule is a small, independent, deterministic unit: given a
``ConstraintContext`` it returns a ``ConstraintResult`` with explicit status,
severity and evidence. Rules must not mutate the context, must not use clocks,
randomness or I/O, and must explain themselves through evidence.
"""

from abc import ABC, abstractmethod

from engine.models.context import ConstraintContext
from engine.constraints.result import ConstraintResult
from engine.constraints.types import ConstraintType


class ConstraintRule(ABC):
    """Abstract base for all constraint rules.

    Deterministic · Independent · Composable · Explainable · Testable ·
    Versionable (each rule carries its own ``rule_version``).
    """

    #: Stable identifier, e.g. "RAILMIND.HARD.BLOCK_DURATION".
    rule_id: str
    #: Per-rule semantic version; bump when the rule's logic or thresholds change.
    rule_version: str
    #: Human-readable name for reports and UI traces.
    name: str
    description: str = ""
    constraint_type: ConstraintType

    @abstractmethod
    def evaluate(self, context: ConstraintContext) -> ConstraintResult:
        """Evaluate this rule against the context. Must be pure/deterministic."""

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<{type(self).__name__} rule_id={self.rule_id!r} type={self.constraint_type.value}>"
