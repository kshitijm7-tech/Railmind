"""Scenario comparison inputs (E04).

E04 consumes E03's already-evaluated public contracts:
``CandidateSolution`` + ``ObjectiveBreakdown``. It never re-derives an
objective value itself — delegation goes through E03's evaluator, which
remains the single source of truth for the §17.5 formula.

``ScenarioCandidate`` is the minimal E04 wrapper: a stable caller-supplied
identity, the candidate solution (carried for context/audit), and the E03
breakdown being compared. Feasibility is OUT OF SCOPE for E04 (PRD §29's
"Constraint status" is reported per plan by the backend integrating E01;
E04 compares the objective among candidates supplied by the caller).
"""

import math
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field, field_validator

from engine.optimization.inputs import CandidateSolution
from engine.optimization.result import ObjectiveBreakdown


class ScenarioCandidate(BaseModel):
    """One candidate plan entering a scenario comparison.

    Identity (``candidate_id``) is caller-supplied and validated non-empty:
    E04 never generates IDs, never invents identities. The full E03
    ``ObjectiveBreakdown`` is preserved verbatim — ranking never reduces a
    candidate to a single number.
    """

    model_config = ConfigDict(frozen=True, validate_default=True)

    candidate_id: str
    solution: CandidateSolution
    objective: ObjectiveBreakdown

    @field_validator("candidate_id")
    @classmethod
    def _candidate_id_nonempty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("candidate_id must be a non-empty, non-blank string")
        return value


def validate_candidates(candidates) -> None:
    """Boundary defense (E04 §11): every objective must be finite.

    E03's evaluator produces finite totals from finite inputs, but E03's
    ``ObjectiveBreakdown`` model does not itself reject non-finite floats —
    so E04 defends its own boundary rather than trusting it. NaN/±inf are
    rejected loudly, never silently zeroed or clamped.
    """
    for candidate in candidates:
        for name in (
            "total_objective",
            "train_delay_component",
            "priority_component",
            "block_count_component",
            "overrun_risk_component",
            "bundling_component",
        ):
            value = getattr(candidate.objective, name)
            if not math.isfinite(value):
                raise ValueError(
                    f"candidate {candidate.candidate_id!r}: objective "
                    f"{name} must be finite; got {value!r} — refusing to "
                    "rank a candidate with a non-finite objective"
                )
