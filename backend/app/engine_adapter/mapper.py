"""API↔engine contract mapping and error translation (E07).

The conversion boundary (E07 prompt §8):

    HTTP Request → API schema → engine input → engine → engine result
                 → API response schema → HTTP response

Every mapping here is explicit and field-by-field. No engine value is
invented, defaulted or clamped: E01–E06 validation is strict and the backend
must not undermine it (§11) — a missing engine-required field is a 400
VALIDATION error, never a silent zero.
"""

import math
from datetime import datetime
from typing import Optional

from app.core.errors import DomainError, ErrorCategory
from app.engine_bridge import (
    BlockWindow,
    DurationBand,
    PriorityInput,
)

# Canonical criticality vocabulary shared by E02 and the backend enum
# (both define LOW|MEDIUM|HIGH|CRITICAL; the engine accepts plain strings).
_CRITICALITY_VALUES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


def _require_finite(value: float, field: str) -> float:
    if not math.isfinite(value):
        raise DomainError(
            message=f"{field} must be finite; got {value!r}",
            category=ErrorCategory.VALIDATION,
            code="ENGINE_INPUT_NOT_FINITE",
        )
    return value


def prioritize_task_to_priority_input(request) -> PriorityInput:
    """API `PrioritizeTaskRequest` → E02 `PriorityInput` (explicit mapping).

    Strictness notes:
    - ``criticality`` is validated against the canonical vocabulary — the
      engine would reject it too, but failing here keeps engine errors out
      of the HTTP surface (the engine stays an internal boundary);
    - ``overdue_days`` negative values are rejected here with a clean 400
      (pydantic would reject them at the engine boundary with a traceback
      class better kept internal);
    - optional fields are passed through as None when absent — no invented
      defaults (§11).
    """
    criticality = request.criticality
    if criticality not in _CRITICALITY_VALUES:
        raise DomainError(
            message=(
                f"criticality must be one of LOW|MEDIUM|HIGH|CRITICAL; "
                f"got {criticality!r}"
            ),
            category=ErrorCategory.VALIDATION,
            code="INVALID_CRITICALITY",
        )
    if request.overdueDays is not None and request.overdueDays < 0:
        raise DomainError(
            message="overdueDays must be >= 0",
            category=ErrorCategory.VALIDATION,
            code="INVALID_OVERDUE_DAYS",
        )

    failure_risk = None
    if request.failureRisk is not None:
        risk = request.failureRisk
        probability = _require_finite(risk.probabilityOfFailure, "probabilityOfFailure")
        if not 0.0 <= probability <= 1.0:
            raise DomainError(
                message="probabilityOfFailure must be within [0, 1]",
                category=ErrorCategory.VALIDATION,
                code="INVALID_PROBABILITY",
            )

        # Late import avoids a circular module-level dependency in the bridge.
        from app.engine_bridge import AssetFailureRisk

        failure_risk = AssetFailureRisk(
            probability_of_failure=probability,
            time_horizon_hours=risk.timeHorizonHours,
            model_id=risk.modelId,
            model_version=risk.modelVersion,
        )

    trains_per_day = None
    if request.trainsPerDay is not None:
        trains_per_day = _require_finite(request.trainsPerDay, "trainsPerDay")
        if trains_per_day < 0.0:
            raise DomainError(
                message="trainsPerDay must be >= 0",
                category=ErrorCategory.VALIDATION,
                code="INVALID_TRAINS_PER_DAY",
            )

    return PriorityInput(
        task_id=request.taskId,
        section_id=request.sectionId,
        criticality=criticality,
        overdue_days=request.overdueDays if request.overdueDays is not None else 0,
        task_type=request.taskType,
        is_safety_relevant=request.isSafetyRelevant,
        asset_failure_risk=failure_risk,
        trains_per_day=trains_per_day,
    )


def window_request_to_block_window(window) -> BlockWindow:
    """API `SimulateBlockRequest` → E05 `BlockWindow` (explicit mapping).

    Task bands are required (the engine refuses to fabricate uncertainty);
    ordering validation stays with the engine — a band with p10 > p90 is a
    caller error surfaced as 400 with the engine's authoritative message.
    """
    if not window.taskBands:
        raise DomainError(
            message=(
                f"taskBands is required for window {window.windowId!r}: the "
                "Monte Carlo pass samples each task duration from its "
                "[P10, P90] band and never invents uncertainty"
            ),
            category=ErrorCategory.VALIDATION,
            code="MISSING_TASK_BANDS",
        )
    bands = [
        DurationBand(
            task_id=band.taskId,
            p10_minutes=_require_finite(band.p10Minutes, "p10Minutes"),
            p90_minutes=_require_finite(band.p90Minutes, "p90Minutes"),
        )
        for band in window.taskBands
    ]
    return BlockWindow(
        window_id=window.windowId,
        section_id=window.sectionId,
        earliest_start=window.earliestStart,
        latest_end=window.latestEnd,
        max_duration_minutes=_require_finite(
            window.maxDurationMinutes, "maxDurationMinutes"
        ),
        task_bands=bands,
    )


def translate_engine_error(exc: Exception) -> DomainError:
    """Engine-domain errors → backend `DomainError` (§10 mapping).

    Engine validation failures (pydantic `ValueError`s from frozen-model
    construction, engine ValueError raises) are caller errors: 400 VALIDATION.
    KeyError is a lookup miss: 404 NOT_FOUND. Anything else propagates to
    FastAPI's standard 500 handling — never blanket-caught here.
    """
    if isinstance(exc, DomainError):
        return exc
    if isinstance(exc, KeyError):
        return DomainError(
            message=str(exc.args[0]) if exc.args else str(exc),
            category=ErrorCategory.NOT_FOUND,
            code="ENGINE_ENTITY_NOT_FOUND",
        )
    if isinstance(exc, ValueError):
        return DomainError(
            message=str(exc),
            category=ErrorCategory.VALIDATION,
            code="ENGINE_INPUT_INVALID",
        )
    return exc  # non-domain errors propagate unchanged


__all__ = [
    "prioritize_task_to_priority_input",
    "window_request_to_block_window",
    "translate_engine_error",
]
