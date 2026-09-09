"""EngineIntegrationService (E07) — thin orchestration facade over the engine.

Responsibilities (backend-owned, §4): engine lifecycle (one predictor
instance per process — construction is O(1), so no premature caching), API→
engine mapping via ``app.engine_adapter.mapper``, engine invocation, and
engine→API response construction. Domain math is NEVER re-implemented here:
every calculation is a delegated engine call (tested in
``backend/tests/test_engine_architecture.py``).
"""

from typing import Optional

from app.engine_adapter.mapper import (
    planner_result_to_response,
    prioritize_task_to_priority_input,
    request_to_planner_input,
    translate_engine_error,
    window_request_to_block_window,
)
from app.engine_bridge import (
    CpSatPlanner,
    DelayModelConfig,
    DurationFeatures,
    DurationPredictionWindow,
    DurationPredictor,
    FailureRiskFeatures,
    FailureRiskPredictor,
    GraphPropagationDelayModel,
    PlannerConfig,
    PriorityEngine,
    PriorityEngineConfig,
    SimulationConfig,
    simulate_plan,
)


def _engine_call(operation):
    """Run one engine operation, translating domain errors to DomainError.

    Covers the WHOLE engine interaction — input mapping and invocation — so
    engine contract violations (invalid vocabulary, inverted bands, bad
    enums) surface as 400 with the engine's authoritative message, never as
    raw tracebacks (§10). Other exceptions propagate unchanged (500).
    """
    try:
        return operation()
    except Exception as exc:  # noqa: BLE001 — translation boundary only
        translated = translate_engine_error(exc)
        if translated is exc:
            raise
        raise translated from exc


class EngineIntegrationService:
    """Facade delegating to E02 priority, E05 simulation, E06 prediction."""

    def __init__(self):
        # E02 engine at the authoritative defaults (PRD FR-MI-001 weights).
        # The facade exposes no hidden overrides — requests carry what they
        # carry; nothing is silently defaulted (§11).
        self._priority_engine = PriorityEngine(PriorityEngineConfig())
        # E06 predictors: O(1) construction, one instance per process (§26).
        self._duration_predictor = DurationPredictor()
        self._failure_risk_predictor = FailureRiskPredictor()
        # E09: the §16.3 delay baseline and the §17 CP-SAT planner. Both are
        # deterministic, stateless-per-call, and O(1) to construct — one
        # instance per process (§26). Requests override only the explicitly
        # declared solver fields (timeout/alternatives/seed); absent values
        # keep the authoritative TRD §65 configuration.
        self._delay_model = GraphPropagationDelayModel(DelayModelConfig())
        self._planner = CpSatPlanner(PlannerConfig())

    # ------------------------------------------------------------------
    # E02 — POST /maintenance/prioritize (TRD §37 Maintenance family)
    # ------------------------------------------------------------------

    def prioritize(self, request):
        """One task → E02 PriorityResult, wrapped in the API schema."""

        def _run():
            engine_input = prioritize_task_to_priority_input(request)
            return self._priority_engine.evaluate(engine_input)

        return _priority_response(_engine_call(_run))

    # ------------------------------------------------------------------
    # E05 — plan/scenario simulate (seed/iterations passed through exactly)
    # ------------------------------------------------------------------

    def simulate(self, windows, iterations: Optional[int] = None, seed: Optional[int] = None):
        """Windows → E05 seeded Monte Carlo → simulation API schema.

        Semantics preserved exactly (§13): the caller's seed and iteration
        count go into validated engine configuration; the backend creates no
        RNG, touches no global state, and never reinterprets probabilities.
        """
        def _run():
            if not windows:
                raise ValueError(
                    "simulate requires at least one block window; an empty "
                    "plan is a caller error, not an empty report"
                )
            block_windows = [window_request_to_block_window(w) for w in windows]
            # Only explicitly supplied values override the authoritative E05
            # defaults (N=200 / seed 0); absent fields stay absent.
            config_kwargs = {}
            if iterations is not None:
                config_kwargs["iterations"] = iterations
            if seed is not None:
                config_kwargs["seed"] = seed
            return simulate_plan(block_windows, SimulationConfig(**config_kwargs))

        return _simulate_response(_engine_call(_run))

    # ------------------------------------------------------------------
    # E06 — deterministic-baseline predictions
    # ------------------------------------------------------------------

    def predict_duration(self, request):
        def _run():
            features = _duration_features_from_request(request)
            window = _duration_window_from_request(request)
            return self._duration_predictor.predict(features, window)

        return _duration_response(_engine_call(_run))

    def predict_failure_risk(self, request):
        def _run():
            features = _failure_features_from_request(request)
            return self._failure_risk_predictor.predict(features)

        return _failure_response(_engine_call(_run))

    # ------------------------------------------------------------------
    # E09 — POST /plans/generate (§17 CP-SAT optimization engine)
    # ------------------------------------------------------------------

    def generate_plan(self, request):
        """Planning instance → E09 CP-SAT plans + exact §17.5 evidence.

        Only explicitly supplied request fields override the authoritative
        TRD §65 solver configuration (timeout 10 s / alternatives 2 / seed 0);
        absent values keep the engine defaults — no backend-invented solver
        settings (§11/§14).
        """

        def _run():
            planner_input = request_to_planner_input(request, self._delay_model)
            config_kwargs = {}
            if request.timeoutSeconds is not None:
                config_kwargs["timeout_seconds"] = request.timeoutSeconds
            if request.alternativeCount is not None:
                config_kwargs["alternative_count"] = request.alternativeCount
            if request.randomSeed is not None:
                config_kwargs["random_seed"] = request.randomSeed
            effective = self._planner.config
            if config_kwargs:
                # Frozen config — explicit-override rebuild, never mutation.
                effective = effective.model_copy(update=config_kwargs)
            # O(1) constructor; keeps the shared instance immutable.
            return CpSatPlanner(effective).plan(planner_input)

        return planner_result_to_response(_engine_call(_run))


# ----------------------------------------------------------------------
# Engine result → API schema builders (the explicit conversion step)
# ----------------------------------------------------------------------


def _priority_response(result):
    from app.api.schemas.engine import PrioritizeTaskResponse

    return PrioritizeTaskResponse(
        taskId=result.task_id,
        priorityScore=result.score,
        priorityClass=result.priority_class,
        factors=[
            {
                "factor": f.factor,
                "rawValue": f.raw_value,
                "rawDescription": f.raw_description,
                "normalizedScore": f.normalized_score,
                "weight": f.weight,
                "contribution": f.contribution,
                "source": f.source,
            }
            for f in result.factor_scores
        ],
        missingFactors=result.missing_factors,
        missingDataPolicy=result.missing_data_policy,
        explanation=result.explanation,
        evidence=result.evidence,
        priorityModelId=result.priority_model_id,
        priorityModelVersion=result.priority_model_version,
        engineVersion=result.engine_version,
    )


def _simulate_response(result):
    from app.api.schemas.engine import SimulateResponse

    return SimulateResponse(
        candidateId=result.candidate_id,
        iterations=result.iterations,
        seed=result.seed,
        distribution=result.distribution,
        planViolationProbability=result.plan_violation_probability,
        anyPlanViolationDraws=result.any_plan_violation_draws,
        constraintExceedances=result.constraint_exceedances,
        blocks=[
            {
                "windowId": p.window_id,
                "sectionId": p.section_id,
                "probabilityOverrun": p.probability_overrun,
                "expectedTotalDuration": p.expected_total_duration,
                "minTotalDuration": p.min_total_duration,
                "maxTotalDuration": p.max_total_duration,
                "p10TotalDuration": p.p10_total_duration,
                "p90TotalDuration": p.p90_total_duration,
                "constraintExceedances": p.constraint_exceedances,
                "violationDraws": p.violation_draws,
            }
            for p in result.block_profiles
        ],
        simulationModelId=result.simulation_model_id,
        simulationModelVersion=result.simulation_model_version,
        engineVersion=result.engine_version,
    )


def _duration_response(result):
    from app.api.schemas.engine import DurationPredictionResponse

    return DurationPredictionResponse(
        taskId=result.task_id,
        predictedDurationMinutes=result.predicted_duration_minutes,
        p10Minutes=result.p10_minutes,
        p90Minutes=result.p90_minutes,
        overrunProbability=result.overrun_probability,
        confidence=result.confidence,
        thresholdMinutes=result.threshold_minutes,
        reasonCodes=result.reason_codes,
        modelId=result.model_id,
        modelVersion=result.model_version,
        algorithm=result.algorithm,
        engineVersion=result.engine_version,
    )


def _failure_response(result):
    from app.api.schemas.engine import FailureRiskPredictionResponse

    return FailureRiskPredictionResponse(
        assetId=result.asset_id,
        probabilityOfFailure=result.probability_of_failure,
        timeHorizonHours=result.time_horizon_hours,
        riskClass=result.risk_class,
        confidence=result.confidence,
        reasonCodes=result.reason_codes,
        modelId=result.model_id,
        modelVersion=result.model_version,
        algorithm=result.algorithm,
        engineVersion=result.engine_version,
    )


# ----------------------------------------------------------------------
# API request → engine input builders (explicit, field-by-field)
# ----------------------------------------------------------------------


def _duration_features_from_request(request) -> DurationFeatures:
    return DurationFeatures(
        task_id=request.taskId,
        task_type=request.taskType,
        department=request.department,
        asset_type=request.assetType,
        section_criticality=request.sectionCriticality,
        crew_size=request.crewSize,
        historical_duration_minutes=request.historicalDurationMinutes,
        time_of_day_minutes=request.timeOfDayMinutes,
        days_since_last_similar_task=request.daysSinceLastSimilarTask,
    )


def _duration_window_from_request(request) -> Optional[DurationPredictionWindow]:
    if request.overrunThresholdMinutes is None and request.latestFinish is None:
        return None
    return DurationPredictionWindow(
        start_at=request.startAt,
        latest_finish=request.latestFinish,
        overrun_threshold_minutes=request.overrunThresholdMinutes,
    )


def _failure_features_from_request(request) -> FailureRiskFeatures:
    return FailureRiskFeatures(
        asset_id=request.assetId,
        asset_age_days=request.assetAgeDays,
        asset_type=request.assetType,
        maintenance_history=request.maintenanceHistory,
        failure_history=request.failureHistory,
        criticality=request.criticality,
        days_since_last_service=request.daysSinceLastService,
        task_backlog=request.taskBacklog,
        condition_score=request.conditionScore,
        time_horizon_hours=request.timeHorizonHours,
    )
