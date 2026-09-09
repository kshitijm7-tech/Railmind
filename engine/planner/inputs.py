"""Planner inputs (E09) — the §17.1–§17.3 model data, contract-first.

Every structure below maps 1:1 to the blueprint's CP-SAT formulation:

- §17.1 sets: tasks (T), candidate block windows (W, each on exactly one
  section), trains (R), departments/crew pools (D);
- §17.2 parameters: ``dur_t``, ``crew_t``/``dept(t)``, ``priority_t`` (from
  E02 — consumed as a score, never recomputed), ``avail_d,shift``,
  ``[e_w, l_w]``/``maxdur_w``, ``delay_pred(w, r)`` (from the E09 §16.3
  baseline — consumed as computed, never re-derived), ``dep(t, t')``;
- §17.3 decision variables are solved, not input — they appear only in the
  result contract.

Validation discipline (E01–E08 convention): frozen contracts, loud
rejection of NaN/±inf, empty ids, inverted bounds, duplicate identities and
cross-reference violations (an assignment referencing an unknown window is
a contract error, never a silent drop).
"""

import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from engine.delay.result import DelayPredictionResult
from engine.priority.result import PriorityResult


def _finite(value: float, name: str) -> float:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite; got {value!r}")
    return value


class TaskInput(BaseModel):
    """One maintenance task (§17.1 T) with its §17.2 parameters.

    Tier-1 time encoding is integer minutes (§17.3: start/end ∈ ℤ), so
    ``duration_minutes`` must be a whole number of minutes — fractional
    durations are rejected loudly rather than silently scaled or truncated.
    """

    model_config = ConfigDict(frozen=True)

    task_id: str
    duration_minutes: float = Field(gt=0.0)  # dur_t
    crew_size: int = Field(default=1, ge=1)  # crew_t
    department: str  # dept(t)
    # §17.2 priority_t: E02's PriorityResult, consumed AS-IS (never a bare
    # score — E03's β term requires factor provenance, and the planner never
    # rebuilds or recomputes priority from task attributes, §9/§16).
    # Required: §17.2 defines priority_t as a model parameter; a caller that
    # cannot supply it runs E02 first (POST /maintenance/prioritize).
    priority: PriorityResult
    # §17.4 c9: latest_finish (mandatory deadline when present).
    latest_finish: Optional[datetime] = None

    @field_validator("task_id", "department")
    @classmethod
    def _ids_nonempty(cls, value: str, info) -> str:
        if not value or not value.strip():
            raise ValueError(f"{info.field_name} must be non-empty")
        return value

    @field_validator("duration_minutes")
    @classmethod
    def _finite_duration(cls, value: float) -> float:
        _finite(value, "duration_minutes")
        if value != int(value):
            raise ValueError(
                f"duration_minutes must be a whole number of minutes "
                f"(§17.3 integer time encoding); got {value!r}"
            )
        return value


class CrewPool(BaseModel):
    """One department's crew availability (§17.1 D, §17.2 avail_d,shift).

    Tier-1 shifts are caller-declared: the pool declares which shifts it
    covers and the crew count available in each. E09 does not model shift
    boundaries itself — it validates consistency, it does not invent them.
    """

    model_config = ConfigDict(frozen=True)

    department: str
    shift_id: str
    available_crew: int = Field(ge=0)

    @field_validator("department", "shift_id")
    @classmethod
    def _ids_nonempty(cls, value: str, info) -> str:
        if not value or not value.strip():
            raise ValueError(f"{info.field_name} must be non-empty")
        return value


class WindowInput(BaseModel):
    """One candidate block window (§17.1 W, §17.2 [e_w, l_w], maxdur_w)."""

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    window_id: str
    section_id: str  # sec(w): each window belongs to exactly one section
    earliest_start: datetime  # e_w
    latest_end: datetime  # l_w
    max_duration_minutes: float = Field(gt=0.0)  # maxdur_w
    # §17.4 c3: departments with qualified crew for work in this window.
    qualified_departments: List[str] = []
    # §17.5 ε term input: cross-department bundling bonus if activated.
    bundle_bonus: float = Field(default=0.0, ge=0.0)
    # §17.5 δ term input: overrun_risk(w), from §16.1 P90 data / E05
    # evidence — caller-supplied, consumed verbatim (never derived here).
    overrun_risk: float = Field(default=0.0, ge=0.0, le=1.0)

    @field_validator("window_id", "section_id")
    @classmethod
    def _ids_nonempty(cls, value: str, info) -> str:
        if not value or not value.strip():
            raise ValueError(f"{info.field_name} must be non-empty")
        return value

    @field_validator("max_duration_minutes", "bundle_bonus", "overrun_risk")
    @classmethod
    def _finite_fields(cls, value: float, info) -> float:
        return _finite(value, info.field_name)

    @field_validator("qualified_departments")
    @classmethod
    def _departments_nonempty(cls, value: List[str]) -> List[str]:
        for department in value:
            if not department or not department.strip():
                raise ValueError("qualified_departments entries must be non-empty")
        return value

    @model_validator(mode="after")
    def _bounds_ordered(self) -> "WindowInput":
        if self.latest_end <= self.earliest_start:
            raise ValueError(
                f"window {self.window_id!r}: latest_end must be strictly "
                "after earliest_start"
            )
        return self


class PlannerInput(BaseModel):
    """The complete §17 model instance handed to the solver.

    Cross-reference integrity is validated here (§21): windows on the same
    section must not have identical ids; task↔window feasibility hints are
    caller knowledge, the solver re-derives feasibility from §17.4.
    """

    model_config = ConfigDict(frozen=True)

    tasks: List[TaskInput]
    windows: List[WindowInput]
    # Caller-supplied run reference (e.g. "PLAN-2026-09-14"); produced plan
    # ids derive from it (``{plan_ref}-alt{n}``). Never invented here.
    plan_ref: Optional[str] = None
    crew_pools: List[CrewPool] = []
    # §17.2 delay_pred(w, r) WITH its §16.3 evidence: window_id -> the E09
    # delay model's verbatim result. The solver consumes the derived
    # ``delay_predictions`` view; the result object rides on activated blocks
    # so the §16.3 provenance survives end-to-end (never recomputed here).
    delay_results: Dict[str, DelayPredictionResult] = {}
    # §17.2 dep(t, t'): t must precede t' (c8) — list of (before, after).
    precedence: List[Tuple[str, str]] = []

    @property
    def delay_predictions(self) -> Dict[str, Dict[str, float]]:
        """Derived §17.2 delay_pred(w, r) view (window -> train -> minutes)."""
        return {
            window_id: {
                record.train_id: record.delay_minutes
                for record in result.trains
            }
            for window_id, result in self.delay_results.items()
        }

    @field_validator("tasks")
    @classmethod
    def _unique_tasks(cls, value: List[TaskInput]) -> List[TaskInput]:
        seen = set()
        for task in value:
            if task.task_id in seen:
                raise ValueError(f"duplicate task_id {task.task_id!r}")
            seen.add(task.task_id)
        return value

    @field_validator("windows")
    @classmethod
    def _unique_windows(cls, value: List[WindowInput]) -> List[WindowInput]:
        seen = set()
        for window in value:
            if window.window_id in seen:
                raise ValueError(f"duplicate window_id {window.window_id!r}")
            seen.add(window.window_id)
        return value

    @field_validator("crew_pools")
    @classmethod
    def _unique_pools(cls, value: List[CrewPool]) -> List[CrewPool]:
        seen = set()
        for pool in value:
            key = (pool.department, pool.shift_id)
            if key in seen:
                raise ValueError(f"duplicate crew pool {key!r}")
            seen.add(key)
        return value

    @model_validator(mode="after")
    def _cross_references(self) -> "PlannerInput":
        if self.plan_ref is not None and not self.plan_ref.strip():
            raise ValueError("plan_ref must be non-empty when supplied")
        task_ids = {t.task_id for t in self.tasks}
        window_ids = {w.window_id for w in self.windows}
        for before, after in self.precedence:
            if before not in task_ids or after not in task_ids:
                raise ValueError(
                    f"precedence references unknown task: ({before!r}, {after!r})"
                )
        for window_id, result in self.delay_results.items():
            if window_id not in window_ids:
                raise ValueError(
                    f"delay_results reference unknown window {window_id!r}"
                )
            for record in result.trains:
                _finite(
                    record.delay_minutes,
                    f"delay_results[{window_id!r}][{record.train_id!r}]",
                )
                if record.delay_minutes < 0.0:
                    raise ValueError(
                        f"delay_results[{window_id!r}][{record.train_id!r}] "
                        "must be nonnegative"
                    )
        return self
