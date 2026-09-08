from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel

T = TypeVar('T')

class PaginationMeta(BaseModel):
    totalItems: int
    page: int
    pageSize: int
    totalPages: int

class ApiMeta(BaseModel):
    timestamp: str
    requestId: str
    version: str

class ApiError(BaseModel):
    code: str
    message: str
    httpStatus: int

class ApiResponse(BaseModel, Generic[T]):
    data: Optional[T] = None
    meta: ApiMeta
    error: Optional[ApiError] = None

class ApiListResponse(BaseModel, Generic[T]):
    data: Optional[List[T]] = None
    pagination: Optional[PaginationMeta] = None
    meta: ApiMeta
    error: Optional[ApiError] = None

class JobAcceptedResponse(BaseModel):
    jobId: str
    status: str = "QUEUED"
    pollEndpoint: str
    estimatedDurationSeconds: Optional[int] = None

class AsyncJob(BaseModel):
    jobId: str
    status: str
    requestedAt: str
    startedAt: Optional[str] = None
    completedAt: Optional[str] = None
    progressPercent: Optional[int] = None
    resultEndpoint: Optional[str] = None
    errorCode: Optional[str] = None
    errorMessage: Optional[str] = None

from app.domain.models.common import TimeInterval
from app.domain.enums import PlanStrategy
from typing import Dict

class GeneratePlanRequest(BaseModel):
    horizon: TimeInterval
    corridorId: str
    strategy: PlanStrategy
    taskIds: Optional[List[str]] = None
    objectiveWeights: Optional[Dict[str, float]] = None
    scenarioContext: Optional[str] = None
    idempotencyKey: Optional[str] = None

class ComparePlansRequest(BaseModel):
    planIds: List[str]
    scenarioContext: Optional[str] = None

from app.domain.models.planning import PlanMetrics

class PlanComparisonEntry(BaseModel):
    planId: str
    planName: str
    strategy: str
    metrics: PlanMetrics
    trainImpactCount: int
    constraintViolations: int
    overrunRisk: float
    recommendationRank: int

class ComparePlansResponse(BaseModel):
    candidates: List[PlanComparisonEntry]
    recommendedPlanId: str
    tradeoffSummary: List[str]
