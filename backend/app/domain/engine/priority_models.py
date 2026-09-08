from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class PriorityClass(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class PriorityFactorResult(BaseModel):
    factor_id: str
    factor_name: str
    raw_value: Any
    normalized_value: float  # 0.0 to 1.0
    weight: float
    contribution: float      # normalized_value * weight
    explanation: str
    evidence: Optional[Dict[str, Any]] = None

class PriorityResult(BaseModel):
    task_id: str
    score: float             # 0.0 to 100.0
    priority_class: PriorityClass
    factors: List[PriorityFactorResult]
    explanation: str
    engine_version: str
    calculated_at: datetime
    data_state: str          # MOCKED | LIVE | SIMULATED

    @property
    def primary_drivers(self) -> List[str]:
        """Returns factor IDs with contribution >= 0.10."""
        return [f.factor_id for f in self.factors if f.contribution >= 0.10]