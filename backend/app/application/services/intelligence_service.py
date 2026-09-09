import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.domain.models.intelligence import (
    DecisionIntelligenceRequest, DecisionIntelligenceResult, EvidenceQuality
)
from app.domain.models.common import Provenance
from app.domain.engine.intelligence.evidence import StandardDecisionEvidenceProvider
from app.domain.engine.intelligence.assessment import DeterministicDecisionAssessmentEngine
from app.domain.enums import DataSource

class DecisionIntelligenceService:
    def __init__(self):
        self.evidence_provider = StandardDecisionEvidenceProvider()
        self.assessment_engine = DeterministicDecisionAssessmentEngine()
        
    def generate_intelligence(
        self, 
        request: DecisionIntelligenceRequest, 
        raw_context: Dict[str, Any]
    ) -> DecisionIntelligenceResult:
        
        # 1. Gather Evidence (Filters out future leakage and scenario mismatches)
        evidence = self.evidence_provider.gather_evidence(request, raw_context)
        
        # 2. Assess Data Quality
        if len(evidence) == 0:
            quality = EvidenceQuality.INSUFFICIENT
            warnings = ["No valid evidence available for candidate plans under the requested scenario and time constraints."]
        elif len(set([ev.source_reference.split('_')[-1] for ev in evidence])) < len(request.candidate_plan_ids):
            quality = EvidenceQuality.LOW
            warnings = ["Partial evidence available. Some candidate plans lack evidence."]
        else:
            quality = EvidenceQuality.HIGH
            warnings = []
            
        # 3. Assess Candidates
        assessment_result = self.assessment_engine.assess_candidates(request, evidence)
        
        # 4. Provenance
        provenance = Provenance(
            state=request.state_mode,
            source=DataSource.SYSTEM,
            generatedAt=datetime.now(timezone.utc),
            generatorVersion="1.0.0"
        )
        
        return DecisionIntelligenceResult(
            decision_id=f"DCI-{uuid.uuid4().hex[:8]}",
            request=request,
            recommended_plan_id=assessment_result["recommended_plan_id"],
            candidates=assessment_result["candidates"],
            evidence=evidence,
            quality_level=quality,
            quality_warnings=warnings,
            primary_drivers=assessment_result["primary_drivers"],
            overall_explanation=assessment_result["overall_explanation"],
            provenance=provenance,
            engine_name=self.assessment_engine.engine_name,
            engine_version=self.assessment_engine.engine_version,
            feature_version=self.assessment_engine.feature_version,
            generated_at=datetime.now(timezone.utc)
        )