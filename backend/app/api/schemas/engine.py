"""E07 API schemas — request/response contracts for the engine boundary.

Compatibility evidence (E07 §5/§20):
- ``frontend/contracts/api/common/envelope.ts`` — camelCase request/response
  fields, ``ApiMeta`` (requestId/timestamp/apiVersion), ``ApiResponse[T]``;
- ``frontend/contracts/ai/predictions.ts`` — camelCase prediction fields
  (model_id→modelId, probability_of_failure→probabilityOfFailure, ...);
- TRD §37 endpoint families for the operations exposed.

Rule (§11, no silent defaults): engine-required numeric fields are REQUIRED
in the API schema; optional engine factors stay Optional and are passed
through as absent (never defaulted to 0/unknown by the backend). Probability
fields carry explicit range constraints so malformed input fails at the
request boundary with a clean 400.
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# E02 — POST /maintenance/prioritize
# ---------------------------------------------------------------------------


class FailureRiskEvidence(BaseModel):
    """Caller-supplied failure-risk evidence (mirrors TS FailureRiskPrediction)."""

    probabilityOfFailure: float = Field(ge=0.0, le=1.0)
    timeHorizonHours: float = Field(default=720.0, gt=0.0)
    modelId: Optional[str] = None
    modelVersion: Optional[str] = None


class PrioritizeTaskRequest(BaseModel):
    """One maintenance task for E02 priority evaluation.

    Required (E02 fail-closed): taskId, sectionId, criticality. Optional
    factors (failureRisk, safety relevance, taskType, trainsPerDay) follow
    E02's missing-data policy — absent means EXCLUDE_FACTOR with renormalised
    weights, never a silent zero.
    """

    taskId: str = Field(min_length=1)
    sectionId: str = Field(min_length=1)
    criticality: str = Field(min_length=1)  # LOW|MEDIUM|HIGH|CRITICAL (validated in adapter)
    overdueDays: Optional[int] = Field(default=None, ge=0)  # PRD: 0 if not overdue
    taskType: Optional[str] = None  # canonical task vocabulary, validated by E02
    isSafetyRelevant: Optional[bool] = None
    failureRisk: Optional[FailureRiskEvidence] = None
    trainsPerDay: Optional[float] = Field(default=None, ge=0.0)


class PriorityFactor(BaseModel):
    """One E02 FactorScore (explanability evidence, verbatim from the engine)."""

    factor: str
    rawValue: Optional[float] = None
    rawDescription: str
    normalizedScore: float
    weight: float
    contribution: float
    source: str


class PrioritizeTaskResponse(BaseModel):
    """E02 PriorityResult — complete explainability + provenance preserved."""

    taskId: str
    priorityScore: float
    priorityClass: str  # LOW|MEDIUM|HIGH|CRITICAL
    factors: List[PriorityFactor]
    missingFactors: List[str] = []
    missingDataPolicy: str
    explanation: str
    evidence: List[str] = []
    priorityModelId: str
    priorityModelVersion: str
    engineVersion: str


# ---------------------------------------------------------------------------
# E05 — plan/scenario simulate
# ---------------------------------------------------------------------------


class TaskDurationBand(BaseModel):
    """One task's [P10, P90] duration band (the E05 sampling input)."""

    taskId: str = Field(min_length=1)
    p10Minutes: float = Field(gt=0.0)
    p90Minutes: float = Field(gt=0.0)


class SimulateBlockRequest(BaseModel):
    """One candidate block window for the §17.6 robustness pass."""

    windowId: str = Field(min_length=1)
    sectionId: str = Field(min_length=1)
    earliestStart: datetime
    latestEnd: datetime
    maxDurationMinutes: float = Field(gt=0.0)
    taskBands: List[TaskDurationBand]


class SimulateRequest(BaseModel):
    """Monte Carlo robustness pass over one or more block windows.

    ``iterations``/``seed`` are OPTIONAL pass-throughs: when absent, the
    authoritative E05 defaults (N=200, seed 0) apply untouched. The backend
    never injects its own seed (§13).
    """

    windows: List[SimulateBlockRequest] = Field(min_length=1)
    iterations: Optional[int] = Field(default=None, ge=1)
    seed: Optional[int] = Field(default=None, ge=0)


class BlockRiskEvidence(BaseModel):
    """Per-block §17.6 evidence (P(overrun) + the numbers behind it)."""

    windowId: str
    sectionId: str
    probabilityOverrun: float
    expectedTotalDuration: float
    minTotalDuration: float
    maxTotalDuration: float
    p10TotalDuration: float
    p90TotalDuration: float
    constraintExceedances: Dict[str, int]
    violationDraws: List[int]


class SimulateResponse(BaseModel):
    """§17.6 result — probabilities, sampling evidence, E05 provenance."""

    candidateId: str
    iterations: int
    seed: int
    distribution: str
    planViolationProbability: float
    anyPlanViolationDraws: int
    constraintExceedances: Dict[str, int]
    blocks: List[BlockRiskEvidence]
    simulationModelId: str
    simulationModelVersion: str
    engineVersion: str


# ---------------------------------------------------------------------------
# E06 — deterministic-baseline predictions
# ---------------------------------------------------------------------------


class DurationPredictionRequest(BaseModel):
    """TRD §13 / blueprint §16.1 duration-prediction features (all required —
    the engine never invents features)."""

    taskId: str = Field(min_length=1)
    taskType: str = Field(min_length=1)
    department: str = Field(min_length=1)
    assetType: str = Field(min_length=1)
    sectionCriticality: str = Field(min_length=1)  # LOW|MEDIUM|HIGH|CRITICAL
    crewSize: int = Field(ge=0)
    historicalDurationMinutes: float = Field(gt=0.0)
    timeOfDayMinutes: float = Field(ge=0.0, lt=1440.0)
    daysSinceLastSimilarTask: float = Field(ge=0.0)
    # Optional overrun context: explicit minute budget, or deadline + start
    # (deadline without start is refused — no threshold is ever guessed).
    overrunThresholdMinutes: Optional[float] = Field(default=None, gt=0.0)
    startAt: Optional[datetime] = None
    latestFinish: Optional[datetime] = None


class DurationPredictionResponse(BaseModel):
    """TRD §13 outputs — algorithm field states the honest baseline status."""

    taskId: str
    predictedDurationMinutes: float
    p10Minutes: float
    p90Minutes: float
    overrunProbability: float
    confidence: float
    thresholdMinutes: float
    reasonCodes: List[str] = []
    modelId: str
    modelVersion: str
    algorithm: str
    engineVersion: str


class FailureRiskPredictionRequest(BaseModel):
    """TRD §15 failure-risk features (all required)."""

    assetId: str = Field(min_length=1)
    assetAgeDays: float = Field(ge=0.0)
    assetType: str = Field(min_length=1)
    maintenanceHistory: int = Field(ge=0)
    failureHistory: int = Field(ge=0)
    criticality: str = Field(min_length=1)  # LOW|MEDIUM|HIGH|CRITICAL
    daysSinceLastService: float = Field(ge=0.0)
    taskBacklog: int = Field(ge=0)
    conditionScore: float = Field(ge=0.0, le=100.0)
    timeHorizonHours: float = Field(default=720.0, gt=0.0)


class FailureRiskPredictionResponse(BaseModel):
    """TRD §15 outputs — failure_risk, risk_class, confidence + identity."""

    assetId: str
    probabilityOfFailure: float
    timeHorizonHours: float
    riskClass: str  # LOW|MEDIUM|HIGH|CRITICAL
    confidence: float
    reasonCodes: List[str] = []
    modelId: str
    modelVersion: str
    algorithm: str
    engineVersion: str


# ---------------------------------------------------------------------------
# E09 — POST /plans/generate (§17 CP-SAT optimization engine)
# ---------------------------------------------------------------------------


class PlanTask(BaseModel):
    """One maintenance task in the §17 planning instance.

    ``priority`` is REQUIRED (the §17.2 parameter priority_t): the caller
    runs ``POST /maintenance/prioritize`` first and passes the **verbatim
    E02 response** through — the engine consumes the full explainable
    PriorityResult (factor provenance + model identity), never a bare
    score, and the backend never invents E02 provenance (§11/§16).
    """

    taskId: str = Field(min_length=1)
    durationMinutes: int = Field(gt=0, description="whole minutes — §17.3 integer time encoding")
    department: str = Field(min_length=1)
    crewSize: int = Field(default=1, ge=1)
    # The verbatim E02 response (§17.2 priority_t with its provenance).
    priority: PrioritizeTaskResponse
    latestFinish: Optional[datetime] = None
    # §17.4 c8 (dep(t, t')): tasks that must not start before this one ends.
    precedes: List[str] = Field(default_factory=list)


class PlanCrewPool(BaseModel):
    """One department's shift availability (§17.1 D / §17.2 avail_d,shift)."""

    department: str = Field(min_length=1)
    shiftId: str = Field(min_length=1)
    availableCrew: int = Field(ge=0)


class PlanWindow(BaseModel):
    """One candidate block window (§17.1 W / §17.2 [e_w, l_w], maxdur_w)."""

    windowId: str = Field(min_length=1)
    sectionId: str = Field(min_length=1)
    earliestStart: datetime
    latestEnd: datetime
    maxDurationMinutes: float = Field(gt=0.0)
    qualifiedDepartments: List[str] = Field(default_factory=list)
    bundleBonus: float = Field(default=0.0, ge=0.0)
    overrunRisk: float = Field(default=0.0, ge=0.0, le=1.0)


class AffectedTrainRequest(BaseModel):
    """One train exposed to a proposed block (§16.3 features)."""

    trainId: str = Field(min_length=1)
    priority: float = Field(ge=0.0)
    route: List[str] = Field(default_factory=list)


class WindowDelayRequest(BaseModel):
    """§16.3 delay-prediction inputs for one window (optional per window).

    When supplied for a window, the CP-SAT objective includes that window's
    predicted train delay (§17.2 delay_pred(w, r)) with its §16.3 evidence
    carried verbatim onto the activated block.
    """

    timeOfDayMinutes: float = Field(ge=0.0, lt=1440.0)
    historicalDelayMinutes: float = Field(ge=0.0)
    affectedTrains: List[AffectedTrainRequest] = Field(default_factory=list)
    adjacency: Dict[str, List[str]] = Field(default_factory=dict)


class PlanGenerationRequest(BaseModel):
    """The §17 planning instance: tasks, windows, crew, optional delays."""

    # Caller-supplied run reference (engine-optional → API-optional, §14);
    # produced plan ids derive from it (``{planRef}-alt{n}``, default base
    # "plan"). Never invented by the backend.
    planRef: Optional[str] = Field(default=None, min_length=1)
    tasks: List[PlanTask] = Field(min_length=1)
    windows: List[PlanWindow] = Field(min_length=1)
    crewPools: List[PlanCrewPool] = Field(default_factory=list)
    delayInputs: Dict[str, WindowDelayRequest] = Field(default_factory=dict)
    # Optional solver overrides; absent values use the authoritative TRD §65
    # configuration (timeout 10 s, alternatives 2, seed 0).
    timeoutSeconds: Optional[float] = Field(default=None, gt=0.0, le=60.0)
    alternativeCount: Optional[int] = Field(default=None, ge=0, le=10)
    randomSeed: Optional[int] = Field(default=None, ge=0)


class PlanAssignment(BaseModel):
    """§17.3 x[t,w] view: one task's assignment (windowId null = unscheduled)."""

    taskId: str
    windowId: Optional[str] = None


class BlockDelayEvidence(BaseModel):
    """§16.3 per-train delay evidence carried verbatim from the baseline."""

    trainId: str
    classification: str
    delayMinutes: float
    propagationHops: int
    priorityProtectionFactor: float


class PlanBlock(BaseModel):
    """One activated block window with its timing and §16.3 evidence."""

    windowId: str
    sectionId: str
    start: datetime
    end: datetime
    assignedTaskIds: List[str]
    assignedWorkMinutes: float
    delayEvidence: Optional[List[BlockDelayEvidence]] = None


class ConstraintTraceRecord(BaseModel):
    """One §17.4 constraint's role in bounding the plan (blueprint §21)."""

    constraintId: str
    description: str
    role: str  # binding | active


class PlanObjectiveBreakdown(BaseModel):
    """The §17.5 decomposition — E03's evaluation, carried verbatim."""

    totalObjective: float
    trainDelayComponent: float
    priorityComponent: float
    blockCountComponent: float
    overrunRiskComponent: float
    bundlingComponent: float
    weights: Dict[str, float]


class GeneratedPlanResponse(BaseModel):
    """One solver-produced plan with its objective + constraint trace."""

    planId: str
    assignments: List[PlanAssignment]
    blocks: List[PlanBlock]
    unscheduledTaskIds: List[str]
    objective: PlanObjectiveBreakdown
    constraintTrace: List[ConstraintTraceRecord]


class SolveEvidenceResponse(BaseModel):
    """TRD §67 reproducibility record for the optimization run."""

    solver: str
    solverVersion: str
    randomSeed: int
    timeoutSeconds: float
    status: str
    wallTimeMs: float
    objectiveWeights: Dict[str, float]
    constraintSetId: str
    constraintSetVersion: str
    engineVersion: str
    plannerModelId: str
    plannerModelVersion: str


class PlanGenerationResponse(BaseModel):
    """Best plan + alternatives + solve evidence (TRD §70: alternatives)."""

    bestPlanId: str
    plans: List[GeneratedPlanResponse]
    evidence: SolveEvidenceResponse
