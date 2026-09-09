from typing import Protocol, List, Dict, Any
from app.domain.models.recovery import (
    Disruption, ImpactAssessment, RecoveryOption, RecoveryAssessmentRequest
)

class ImpactAssessmentEngine(Protocol):
    def assess_impact(
        self,
        disruption: Disruption,
        raw_context: Dict[str, Any]
    ) -> ImpactAssessment:
        ...

class RecoveryCandidateGenerator(Protocol):
    engine_name: str
    engine_version: str
    
    def generate_candidates(
        self,
        assessment: ImpactAssessment,
        request: RecoveryAssessmentRequest,
        raw_context: Dict[str, Any]
    ) -> List[RecoveryOption]:
        ...