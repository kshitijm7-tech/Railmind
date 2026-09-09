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

from app.core.errors import DomainError, ErrorCategory
from app.engine_bridge import (
    AffectedTrain,
    BlockWindow,
    CrewPool,
    DelayFeatures,
    DurationBand,
    FactorScore,
    PlannerInput,
    PriorityInput,
    PriorityResult,
    TaskInput,
    WindowInput,
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


# ---------------------------------------------------------------------------
# E09 — POST /plans/generate (§17 CP-SAT optimization engine)
# ---------------------------------------------------------------------------


def _priority_result_from_response(task) -> PriorityResult:
    """Verbatim E02 API response → engine PriorityResult (field-by-field).

    The caller passes the exact ``PrioritizeTaskResponse`` it received from
    ``POST /maintenance/prioritize``; this rebuilds the engine contract the
    §17.2 priority_t parameter requires — every field explicit, nothing
    invented (factor contributions and model identity ride through so E03's
    β-term provenance survives the full HTTP round-trip).
    """
    p = task.priority
    return PriorityResult(
        task_id=p.taskId,
        score=p.priorityScore,
        priority_class=p.priorityClass,
        factor_scores=[
            FactorScore(
                factor=f.factor,
                raw_value=f.rawValue,
                raw_description=f.rawDescription,
                normalized_score=f.normalizedScore,
                weight=f.weight,
                contribution=f.contribution,
                source=f.source,
            )
            for f in p.factors
        ],
        missing_factors=list(p.missingFactors),
        missing_data_policy=p.missingDataPolicy,
        explanation=p.explanation,
        evidence=list(p.evidence),
        # metadata is request-derived context not carried over HTTP (the E02
        # response schema does not include it); E03's β term consumes only
        # score + factor provenance, all of which is present.
        metadata={},
    )


def _planning_task_to_task_input(task, task_index: int) -> TaskInput:
    """API `PlanTask` → E09 `TaskInput` (explicit mapping).

    Cross-references are validated here with clean 400s (the engine would
    also reject them, but with messages naming engine internals).
    """
    priority = _priority_result_from_response(task)
    if priority.task_id != task.taskId:
        raise DomainError(
            message=(
                f"tasks[{task_index}]: priority.taskId ({priority.task_id!r}) "
                f"does not match taskId ({task.taskId!r}) — pass the E02 "
                "response produced for this exact task"
            ),
            category=ErrorCategory.VALIDATION,
            code="PRIORITY_TASK_MISMATCH",
        )
    return TaskInput(
        task_id=task.taskId,
        duration_minutes=float(task.durationMinutes),
        crew_size=task.crewSize,
        department=task.department,
        priority=priority,
        latest_finish=task.latestFinish,
    )


def _planning_window_to_window_input(window) -> WindowInput:
    """API `PlanWindow` → E09 `WindowInput` (explicit mapping)."""
    return WindowInput(
        window_id=window.windowId,
        section_id=window.sectionId,
        earliest_start=window.earliestStart,
        latest_end=window.latestEnd,
        max_duration_minutes=_require_finite(
            window.maxDurationMinutes, "maxDurationMinutes"
        ),
        qualified_departments=list(window.qualifiedDepartments),
        bundle_bonus=_require_finite(window.bundleBonus, "bundleBonus"),
        overrun_risk=_require_finite(window.overrunRisk, "overrunRisk"),
    )


def _crew_pool_to_crew_pool(pool) -> CrewPool:
    """API `PlanCrewPool` → E09 `CrewPool` (explicit mapping)."""
    return CrewPool(
        department=pool.department,
        shift_id=pool.shiftId,
        available_crew=pool.availableCrew,
    )


def request_to_planner_input(request, delay_model) -> PlannerInput:
    """API `PlanGenerationRequest` → E09 `PlannerInput`.

    The §16.3 delay pass is an internal engine step, not an API-mapped
    computation: when ``delayInputs`` are supplied for a window, the delay
    model runs here (inside the adapter's engine-delegation boundary) and
    the verbatim DelayPredictionResult is attached — the solver consumes
    delay predictions as computed, never re-derives them.
    """
    tasks = [
        _planning_task_to_task_input(t, i) for i, t in enumerate(request.tasks)
    ]
    windows = [_planning_window_to_window_input(w) for w in request.windows]
    crew_pools = [_crew_pool_to_crew_pool(p) for p in request.crewPools]

    delay_results = {}
    for window_id, delay_request in request.delayInputs.items():
        window = next(
            (w for w in request.windows if w.windowId == window_id), None
        )
        if window is None:
            raise DomainError(
                message=(
                    f"delayInputs reference unknown window {window_id!r} — "
                    "delay predictions require the window they belong to"
                ),
                category=ErrorCategory.VALIDATION,
                code="DELAY_INPUT_UNKNOWN_WINDOW",
            )
        features = DelayFeatures(
            window_id=window_id,
            section_id=window.sectionId,
            earliest_start=window.earliestStart,
            latest_end=window.latestEnd,
            time_of_day_minutes=_require_finite(
                delay_request.timeOfDayMinutes, "timeOfDayMinutes"
            ),
            historical_delay_minutes=_require_finite(
                delay_request.historicalDelayMinutes, "historicalDelayMinutes"
            ),
            affected_trains=[
                AffectedTrain(
                    train_id=tr.trainId,
                    priority=_require_finite(tr.priority, "priority"),
                    route=list(tr.route),
                )
                for tr in delay_request.affectedTrains
            ],
            adjacency={
                section: list(neighbors)
                for section, neighbors in delay_request.adjacency.items()
            },
        )
        delay_results[window_id] = delay_model.predict(features)

    precedence = [
        (task.taskId, successor)
        for task in request.tasks
        for successor in task.precedes
    ]

    return PlannerInput(
        tasks=tasks,
        windows=windows,
        plan_ref=request.planRef,
        crew_pools=crew_pools,
        delay_results=delay_results,
        precedence=precedence,
    )


def generated_plan_to_response(plan) -> "GeneratedPlanResponse":
    """Engine `GeneratedPlan` → API `GeneratedPlanResponse` (verbatim carry)."""
    from app.api.schemas.engine import GeneratedPlanResponse

    objective = plan.objective
    return GeneratedPlanResponse(
        planId=plan.plan_id,
        assignments=[
            {"taskId": a.task_id, "windowId": a.window_id}
            for a in plan.assignments
        ],
        blocks=[
            {
                "windowId": b.window_id,
                "sectionId": b.section_id,
                "start": b.start,
                "end": b.end,
                "assignedTaskIds": list(b.assigned_task_ids),
                "assignedWorkMinutes": b.assigned_work_minutes,
                "delayEvidence": (
                    [
                        {
                            "trainId": r.train_id,
                            "classification": r.classification,
                            "delayMinutes": r.delay_minutes,
                            "propagationHops": r.propagation_hops,
                            "priorityProtectionFactor": r.priority_protection_factor,
                        }
                        for r in b.delay_evidence.trains
                    ]
                    if b.delay_evidence is not None
                    else None
                ),
            }
            for b in plan.blocks
        ],
        unscheduledTaskIds=list(plan.unscheduled_task_ids),
        objective={
            "totalObjective": objective.total_objective,
            "trainDelayComponent": objective.train_delay_component,
            "priorityComponent": objective.priority_component,
            "blockCountComponent": objective.block_count_component,
            "overrunRiskComponent": objective.overrun_risk_component,
            "bundlingComponent": objective.bundling_component,
            "weights": dict(objective.weights),
        },
        constraintTrace=[
            {
                "constraintId": c.constraint_id,
                "description": c.description,
                "role": c.role,
            }
            for c in plan.constraint_trace
        ],
    )


def planner_result_to_response(result) -> "PlanGenerationResponse":
    """Engine `PlannerResult` → API `PlanGenerationResponse`.

    Best plan id and evidence are carried verbatim — the backend never
    re-ranks, re-times or re-seeds a solver outcome.
    """
    from app.api.schemas.engine import PlanGenerationResponse, SolveEvidenceResponse

    evidence = result.evidence
    return PlanGenerationResponse(
        bestPlanId=result.best_plan_id,
        plans=[generated_plan_to_response(p) for p in result.plans],
        evidence=SolveEvidenceResponse(
            solver=evidence.solver,
            solverVersion=evidence.solver_version,
            randomSeed=evidence.random_seed,
            timeoutSeconds=evidence.timeout_seconds,
            status=evidence.status,
            wallTimeMs=evidence.wall_time_ms,
            objectiveWeights=dict(evidence.objective_weights),
            constraintSetId=evidence.constraint_set_id,
            constraintSetVersion=evidence.constraint_set_version,
            engineVersion=evidence.engine_version,
            plannerModelId=evidence.planner_model_id,
            plannerModelVersion=evidence.planner_model_version,
        ),
    )


__all__ = [
    "prioritize_task_to_priority_input",
    "window_request_to_block_window",
    "translate_engine_error",
    "request_to_planner_input",
    "planner_result_to_response",
]
