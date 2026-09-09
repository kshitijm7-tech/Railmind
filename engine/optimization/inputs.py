"""Optimization input models (E03).

Narrow, immutable inputs for the §17.5 objective evaluation. Existing
contracts are reused wherever they exist:

- ``PriorityResult`` comes from E02's public contract (engine.priority) and is
  consumed as-is — never recomputed, never rebuilt from task attributes.
- Assignment inputs mirror the blueprint §17.3 decision variables
  (``x[t,w]``, ``y[w]``, ``unscheduled[t]``) at the evaluation level: they
  describe a candidate solution, they do not solve anything.

All numeric inputs are validated nonnegative (the objective terms are
magnitudes; the §17.5 sign convention is applied once, in the evaluator) and
finite (NaN/inf are rejected at the boundary — §17 numerical safety).
"""

import math
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from engine.priority.result import PriorityResult


def _finite_nonnegative(name: str):
    def check(value: float) -> float:
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite; got {value!r}")
        if value < 0.0:
            raise ValueError(f"{name} must be nonnegative; got {value!r}")
        return value

    return check


class TaskAssignment(BaseModel):
    """A task's assignment in the candidate solution (§17.3 x[t,w] view).

    ``priority`` carries the E02 result for this task when it is unscheduled
    (the β term applies to ``unscheduled[t]`` in §17.5). Scheduled tasks do
    not contribute to the β term but their results may be carried for
    reporting. E03 never recomputes a priority; a missing PriorityResult for
    an unscheduled task is a contract error, not a zero.
    """

    # validate_default ensures the ``priority`` validator also fires when the
    # field is simply omitted (pydantic v2 skips validators for defaults), so
    # an unscheduled task can never silently reach the evaluator unvalidated.
    model_config = ConfigDict(frozen=True, validate_default=True)

    task_id: str
    unscheduled: bool
    priority: Optional[PriorityResult] = None

    @field_validator("priority")
    @classmethod
    def _priority_required_when_unscheduled(
        cls, value: Optional[PriorityResult], info
    ) -> Optional[PriorityResult]:
        if info.data.get("unscheduled") and value is None:
            raise ValueError(
                f"unscheduled task {info.data.get('task_id')!r} requires its "
                "E02 PriorityResult (the §17.5 β term needs priority_score); "
                "refusing to substitute a default value"
            )
        return value

    @field_validator("task_id")
    @classmethod
    def _task_id_nonempty(cls, value: str) -> str:
        if not value:
            raise ValueError("task_id must be non-empty")
        return value


class BlockActivation(BaseModel):
    """An activated maintenance block in the candidate solution (§17.3 y[w])."""

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    window_id: str
    # Bundled cross-department bonus for this window (§17.5 ε term input).
    bundle_bonus: float = Field(default=0.0, ge=0.0)
    # Predicted overrun probability for the window (§17.5 δ term input).
    overrun_risk: float = Field(default=0.0, ge=0.0, le=1.0)

    @field_validator("bundle_bonus", "overrun_risk")
    @classmethod
    def _finite(cls, value: float, info) -> float:
        if not math.isfinite(value):
            raise ValueError(f"{info.field_name} must be finite; got {value!r}")
        return value


class CandidateSolution(BaseModel):
    """One candidate plan to evaluate against the §17.5 objective."""

    model_config = ConfigDict(frozen=True)

    plan_id: str
    assignments: List[TaskAssignment] = []
    blocks: List[BlockActivation] = []
    # Total predicted train delay in minutes (Σ_r delay_r, §17.5 α term input).
    total_train_delay_minutes: float = Field(default=0.0, ge=0.0)

    @field_validator("total_train_delay_minutes")
    @classmethod
    def _finite_delay(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError(f"total_train_delay_minutes must be finite; got {value!r}")
        return value

    @field_validator("plan_id")
    @classmethod
    def _plan_id_nonempty(cls, value: str) -> str:
        if not value:
            raise ValueError("plan_id must be non-empty")
        return value

    @property
    def unscheduled_tasks(self) -> List[TaskAssignment]:
        return [a for a in self.assignments if a.unscheduled]
