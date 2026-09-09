"""Constraint result model — the engine's explainability contract.

Every result carries the rule identity (rule_id, rule_version, constraint
type), an explicit status, severity, a human-readable message, a structured
explanation, affected entities and typed evidence, so the backend and the
future optimizer (E03) can consume results without re-deriving them.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict

from engine.constraints.severity import ConstraintSeverity
from engine.constraints.types import ConstraintType
from engine._version import CONSTRAINT_SET_ID, CONSTRAINT_SET_VERSION, ENGINE_VERSION


class ConstraintEvidence(BaseModel):
    """One typed fact supporting a result (blueprint §21 evidence items)."""

    model_config = ConfigDict(frozen=True)

    source: str
    description: str
    quantity: Optional[float] = None


class ConstraintResult(BaseModel):
    """Outcome of evaluating one rule against one context.

    Mirrors the semantics of ``frontend/contracts/planning/constraint.ts``
    (``constraint_id`` / ``is_satisfied`` / ``violation_degree`` /
    ``description``) and extends them with the identity, severity and evidence
    the project's explainability requirements demand.
    """

    model_config = ConfigDict(frozen=False)

    rule_id: str
    rule_version: str
    constraint_type: ConstraintType
    status: str  # PASS | FAIL | WARNING (validated by model_post_init)
    severity: ConstraintSeverity
    message: str
    explanation: str
    affected_entities: List[str] = []
    evidence: List[ConstraintEvidence] = []
    violation_degree: Optional[float] = None
    metadata: Dict[str, Any] = {}
    constraint_set_id: str = CONSTRAINT_SET_ID
    constraint_set_version: str = CONSTRAINT_SET_VERSION
    engine_version: str = ENGINE_VERSION

    @property
    def is_satisfied(self) -> bool:
        """Canonical-contract compatibility: PASS/WARNING are satisfied."""
        return self.status in ("PASS", "WARNING")

    @property
    def violation_degree_or_zero(self) -> float:
        return self.violation_degree if self.violation_degree is not None else 0.0


class ConstraintEvaluation(BaseModel):
    """Aggregated evaluation of a rule set against one context.

    Feasibility semantics (E01 §8): ``feasible`` is true iff no HARD rule has
    FAIL status. SOFT results never affect feasibility.
    """

    constraint_set_id: str = CONSTRAINT_SET_ID
    constraint_set_version: str = CONSTRAINT_SET_VERSION
    engine_version: str = ENGINE_VERSION
    results: List[ConstraintResult] = []

    @property
    def hard_failures(self) -> List[ConstraintResult]:
        return [r for r in self.results if r.constraint_type is ConstraintType.HARD and r.status == "FAIL"]

    @property
    def warnings(self) -> List[ConstraintResult]:
        return [r for r in self.results if r.status == "WARNING"]

    @property
    def feasible(self) -> bool:
        return not self.hard_failures


class EngineError(Exception):
    """Raised when the engine is used in an unsupported way."""
