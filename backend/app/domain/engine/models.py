from enum import Enum
from typing import List, Any, Dict, Optional
from pydantic import BaseModel

class ConstraintSeverity(str, Enum):
    HARD = "HARD"
    SOFT = "SOFT"

class ConstraintStatus(str, Enum):
    FEASIBLE = "FEASIBLE"
    INFEASIBLE = "INFEASIBLE"
    FEASIBLE_WITH_WARNINGS = "FEASIBLE_WITH_WARNINGS"

class ConstraintViolation(BaseModel):
    rule_id: str
    severity: ConstraintSeverity
    message: str
    evidence: Optional[Dict[str, Any]] = None

class EvaluationContext(BaseModel):
    task: Any
    windows: List[Any]
    paths: List[Any]
    section_id: str

class EvaluationResult(BaseModel):
    status: ConstraintStatus
    violations: List[ConstraintViolation]
