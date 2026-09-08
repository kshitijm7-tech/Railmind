from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from app.domain.engine.models import EvaluationContext, EvaluationResult
from app.domain.models.planning import CandidateBlockWindow
from app.api.models import ApiResponse
from app.domain.engine.core import ConstraintEngine
from app.domain.engine.rules import OperationalWindowRule, MaintenanceDurationRule, TrainPathConflictRule, PreferredWindowRule

router = APIRouter()
engine = ConstraintEngine([
    OperationalWindowRule(),
    MaintenanceDurationRule(),
    TrainPathConflictRule(),
    PreferredWindowRule()
])

class EvaluateRequest(BaseModel):
    candidate: CandidateBlockWindow
    context: EvaluationContext

@router.post("/constraints/evaluate", response_model=ApiResponse[EvaluationResult])
def evaluate_constraints(req: EvaluateRequest):
    result = engine.evaluate_candidate(req.candidate, req.context)
    return ApiResponse(
        success=True,
        data=result,
        error=None
    )
