"""Engine intelligence endpoints (E07) — thin HTTP boundary over the engine.

TRD §37 endpoint families served here:
- ``POST /api/v1/maintenance/prioritize`` (Maintenance family → E02);
- ``POST /api/v1/plans/{plan_id}/simulate`` (Plans family → E05);
- ``POST /api/v1/scenarios`` + ``POST /api/v1/scenarios/{scenario_id}/simulate``
  (Scenarios family → E04/E05 stateless pass-through).

The router owns HTTP only: envelope construction (ApiResponse + ApiMeta),
service lookup, and error propagation. All domain math is delegated to the
engine via ``EngineIntegrationService`` (E07 §3/§4 — wrap, never duplicate).
"""

from datetime import datetime, timezone
import uuid

from fastapi import APIRouter, Depends, Path

from app.api.models import ApiError, ApiMeta, ApiResponse
from app.api.schemas.engine import (
    DurationPredictionRequest,
    DurationPredictionResponse,
    FailureRiskPredictionRequest,
    FailureRiskPredictionResponse,
    PlanGenerationRequest,
    PlanGenerationResponse,
    PrioritizeTaskRequest,
    PrioritizeTaskResponse,
    SimulateRequest,
    SimulateResponse,
)
from app.api.dependencies import get_engine_integration_service
from app.core.errors import DomainError, ErrorCategory
from app.engine_adapter.service import EngineIntegrationService

router = APIRouter()


def get_meta() -> ApiMeta:
    """Request metadata per the existing backend convention (system.py)."""
    return ApiMeta(
        timestamp=datetime.now(timezone.utc).isoformat(),
        requestId=str(uuid.uuid4()),
        version="v1.0.0",
    )


def _ok(data) -> ApiResponse:
    return ApiResponse(data=data, meta=get_meta())


@router.post(
    "/maintenance/prioritize",
    response_model=ApiResponse[PrioritizeTaskResponse],
    summary="Evaluate maintenance priority for one task (E02 engine)",
    responses={400: {"model": ApiResponse}},
)  # TRD §37 Maintenance family: POST /maintenance/prioritize
def prioritize_task(
    request: PrioritizeTaskRequest,
    service: EngineIntegrationService = Depends(get_engine_integration_service),
):
    """Deterministic E02 priority with full factor explainability.

    Invalid criticality/overdue/numeric values fail with 400 and the
    engine's authoritative validation message (no silent defaults).
    """
    result = service.prioritize(request)
    return _ok(result)


@router.post(
    "/plans/{plan_id}/simulate",
    response_model=ApiResponse[SimulateResponse],
    summary="Run the §17.6 Monte Carlo robustness pass for a plan (E05 engine)",
    responses={400: {"model": ApiResponse}},
)
def simulate_plan_endpoint(
    request: SimulateRequest,
    plan_id: str = Path(..., min_length=1),
    service: EngineIntegrationService = Depends(get_engine_integration_service),
):
    """Seeded Monte Carlo over the request's block windows.

    ``plan_id`` identifies the candidate for provenance/audit and is carried
    verbatim as the result's ``candidateId``. Caller-supplied seed and
    iteration count are passed through to the engine exactly (no backend-side
    RNG, §13); absent values use the authoritative E05 defaults (N=200/0).
    """
    result = service.simulate(
        request.windows, iterations=request.iterations, seed=request.seed
    )
    stamped = result.model_copy(update={"candidateId": plan_id})
    return _ok(stamped)


@router.post(
    "/scenarios",
    response_model=ApiResponse[dict],
    summary="Register a stateless scenario identity (E04/E05 pass-through)",
    responses={400: {"model": ApiResponse}},
)
def create_scenario(request: dict):
    """E07 Tier-1 reality (§15/§16): E04 compares caller-supplied candidate
    solutions and E05 consumes caller-supplied windows — there is no scenario
    state to store. This endpoint validates the identity envelope and returns
    it; the authoritative simulation/comparison state family remains a later
    phase (documented in docs/E07_Report.md §11)."""
    scenario_id = request.get("scenarioId") if isinstance(request, dict) else None
    if not scenario_id or not isinstance(scenario_id, str):
        raise DomainError(
            message="scenarioId (non-empty string) is required",
            category=ErrorCategory.VALIDATION,
            code="INVALID_SCENARIO_ID",
        )
    return _ok({"scenarioId": scenario_id, "status": "REGISTERED"})


@router.post(
    "/scenarios/{scenario_id}/simulate",
    response_model=ApiResponse[SimulateResponse],
    summary="Run the §17.6 robustness pass under a scenario identity (E05 engine)",
    responses={400: {"model": ApiResponse}},
)
def simulate_scenario_endpoint(
    request: SimulateRequest,
    scenario_id: str = Path(..., min_length=1),
    service: EngineIntegrationService = Depends(get_engine_integration_service),
):
    """Same deterministic E05 pass as the plan endpoint; ``scenario_id`` is
    carried verbatim as the result's ``candidateId`` so risk evidence stays
    traceable to the scenario the caller named (§14 candidate association)."""
    result = service.simulate(
        request.windows, iterations=request.iterations, seed=request.seed
    )
    stamped = result.model_copy(update={"candidateId": scenario_id})
    return _ok(stamped)


@router.post(
    "/predictions/duration",
    response_model=ApiResponse[DurationPredictionResponse],
    summary="Predict maintenance task duration (E06 Model 1, deterministic baseline)",
    responses={400: {"model": ApiResponse}},
)
def predict_duration(
    request: DurationPredictionRequest,
    service: EngineIntegrationService = Depends(get_engine_integration_service),
):
    """Deterministic-baseline duration prediction.

    The response's ``algorithm`` field honestly reports the predictor type
    (``deterministic-rules``); no trained-ML availability is claimed (§14).
    """
    result = service.predict_duration(request)
    return _ok(result)


@router.post(
    "/predictions/failure-risk",
    response_model=ApiResponse[FailureRiskPredictionResponse],
    summary="Predict asset failure risk (E06 Model 4, deterministic baseline)",
    responses={400: {"model": ApiResponse}},
)
def predict_failure_risk(
    request: FailureRiskPredictionRequest,
    service: EngineIntegrationService = Depends(get_engine_integration_service),
):
    """Deterministic-baseline failure-risk prediction with E06-owned risk
    classification. ``algorithm`` reports ``deterministic-rules`` — never a
    fabricated trained-model label (§14)."""
    result = service.predict_failure_risk(request)
    return _ok(result)


@router.post(
    "/plans/generate",
    response_model=ApiResponse[PlanGenerationResponse],
    summary="Generate optimized maintenance plans (E09 CP-SAT engine, §17)",
    responses={400: {"model": ApiResponse}},
)  # TRD §37 Plans family: POST /plans/generate
def generate_plans(
    request: PlanGenerationRequest,
    service: EngineIntegrationService = Depends(get_engine_integration_service),
):
    """Solve the §17 CP-SAT planning instance.

    Consumes verbatim E02 priority responses (§17.2 priority_t) and optional
    §16.3 delay inputs; returns the best plan plus near-optimal alternatives,
    each ranked by E03's exact §17.5 objective, with the TRD §67 solve-evidence
    record (solver, seed, wall time, versions). Only explicitly supplied
    request fields override the authoritative TRD §65 solver configuration.
    """
    result = service.generate_plan(request)
    return _ok(result)
