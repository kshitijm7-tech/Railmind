import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.domain.models.recovery import (
    RecoveryAssessmentRequest, RecoveryAssessmentResult,
    DisruptionStatus
)
from app.domain.models.common import Provenance
from app.domain.enums import DataSource
from app.domain.engine.recovery.baseline import (
    DeterministicImpactAssessmentEngine, DeterministicRecoveryCandidateGenerator
)

class RecoveryService:
    def __init__(self):
        self.impact_engine = DeterministicImpactAssessmentEngine()
        self.candidate_generator = DeterministicRecoveryCandidateGenerator()
        
    def assess_recovery(
        self,
        request: RecoveryAssessmentRequest,
        raw_context: Dict[str, Any]
    ) -> RecoveryAssessmentResult:
        
        # 1. State / Scenario Isolation Check
        if request.disruption.state_mode != raw_context.get("expected_state_mode", request.disruption.state_mode):
            raise ValueError("State mode mismatch between disruption and provided context.")
            
        # 2. Temporal Validity Check
        cutoff = request.requested_at
        if request.disruption.start_time > cutoff:
            raise ValueError("Cannot assess future disruption. Temporal leakage detected.")
        
        # 3. Impact Assessment
        impact = self.impact_engine.assess_impact(request.disruption, raw_context)
        
        # 4. Candidate Generation
        options = []
        if request.disruption.status != DisruptionStatus.RESOLVED:
            options = self.candidate_generator.generate_candidates(impact, request, raw_context)
            
        # 5. Determine Quality
        quality = "HIGH"
        warnings = []
        if not options:
            quality = "LOW"
            warnings.append("No recovery options could be generated.")
            
        if not raw_context.get("constraints_validated", False):
            # Without P09 validation, candidates are inherently risky/unverified
            if quality == "HIGH":
                quality = "MEDIUM"
            warnings.append("Candidates have not been validated against P09 rules engine.")
            
        provenance = Provenance(
            state=request.disruption.state_mode,
            source=DataSource.SYSTEM,
            generatedAt=datetime.now(timezone.utc),
            generatorVersion="1.0.0"
        )
        
        return RecoveryAssessmentResult(
            recovery_id=f"RCA-{uuid.uuid4().hex[:8]}",
            disruption=request.disruption,
            impact_assessment=impact,
            recovery_options=options,
            recommended_option_id=None, # P18 does not recommend. P17 does. P18 just generates options.
            quality=quality,
            warnings=warnings,
            provenance=provenance,
            engine_version="1.0.0",
            generated_at=datetime.now(timezone.utc)
        )