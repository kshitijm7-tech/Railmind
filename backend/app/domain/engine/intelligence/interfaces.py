from typing import Protocol, List, Dict, Any
from app.domain.models.intelligence import DecisionIntelligenceRequest, CandidateAssessment, DecisionEvidence, EvidenceQuality

class DecisionEvidenceProvider(Protocol):
    def gather_evidence(
        self,
        request: DecisionIntelligenceRequest,
        raw_context: Dict[str, Any]
    ) -> List[DecisionEvidence]:
        """Extracts and normalizes evidence from raw context, applying temporal safety."""
        ...

class DecisionAssessmentEngine(Protocol):
    engine_name: str
    engine_version: str
    feature_version: str
    
    def assess_candidates(
        self,
        request: DecisionIntelligenceRequest,
        evidence: List[DecisionEvidence]
    ) -> Dict[str, Any]:
        """
        Returns a dict containing:
        - recommended_plan_id: Optional[str]
        - candidates: List[CandidateAssessment]
        - primary_drivers: List[str]
        - overall_explanation: str
        """
        ...