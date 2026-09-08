import uuid
from typing import Dict, Any, List
from datetime import datetime, timezone
from app.domain.enums import DataSource
from app.domain.models.intelligence import DecisionIntelligenceRequest, DecisionEvidence, EvidenceType
from app.domain.models.common import Provenance
from app.domain.engine.intelligence.interfaces import DecisionEvidenceProvider

class StandardDecisionEvidenceProvider(DecisionEvidenceProvider):
    def gather_evidence(
        self,
        request: DecisionIntelligenceRequest,
        raw_context: Dict[str, Any]
    ) -> List[DecisionEvidence]:
        evidence_list = []
        cutoff = request.requested_at
        state = request.state_mode
        scenario = request.scenario_id
        
        # 1. Gather Simulation Evidence
        sim_results = raw_context.get("simulations", {})
        for plan_id, sim in sim_results.items():
            if sim.get("timestamp") and sim["timestamp"] >= cutoff:
                continue # Temporal leakage
            if sim.get("state") != state:
                continue # Scenario isolation
            
            # Extract delay as negative evidence
            delay = sim.get("total_delay_minutes", 0)
            evidence_list.append(DecisionEvidence(
                evidence_id=f"EVI-{uuid.uuid4().hex[:8]}",
                evidence_type=EvidenceType.SIMULATION,
                source_reference=f"SIM_{plan_id}",
                summary_value=delay,
                direction=-1,
                severity="HIGH" if delay > 60 else "MEDIUM",
                timestamp=sim.get("timestamp", cutoff),
                provenance=Provenance(
                    state=state,
                    source=DataSource.SYSTEM,
                    generatedAt=datetime.now(timezone.utc)
                ),
                explanation=f"Simulation predicts {delay} mins of total train delay."
            ))
            
            # Extract maintenance completed as positive evidence
            completed = sim.get("completed_maintenance_tasks", 0)
            evidence_list.append(DecisionEvidence(
                evidence_id=f"EVI-{uuid.uuid4().hex[:8]}",
                evidence_type=EvidenceType.SIMULATION,
                source_reference=f"SIM_MAINT_{plan_id}",
                summary_value=completed,
                direction=1,
                severity="HIGH",
                timestamp=sim.get("timestamp", cutoff),
                provenance=Provenance(
                    state=state,
                    source=DataSource.SYSTEM,
                    generatedAt=datetime.now(timezone.utc)
                ),
                explanation=f"Simulation indicates {completed} tasks can be successfully completed."
            ))

        # 2. Gather Risk Evidence (Risk level maps to negative evidence)
        risk_results = raw_context.get("risks", {})
        for plan_id, risk in risk_results.items():
            if risk.get("timestamp") and risk["timestamp"] >= cutoff:
                continue
            if risk.get("state") != state:
                continue
                
            risk_score = risk.get("risk_score", 0)
            evidence_list.append(DecisionEvidence(
                evidence_id=f"EVI-{uuid.uuid4().hex[:8]}",
                evidence_type=EvidenceType.RISK,
                source_reference=f"RSK_{plan_id}",
                summary_value=risk_score,
                direction=-1,
                severity="HIGH" if risk_score >= 75 else ("MEDIUM" if risk_score >= 50 else "LOW"),
                timestamp=risk.get("timestamp", cutoff),
                provenance=Provenance(
                    state=state,
                    source=DataSource.SYSTEM,
                    generatedAt=datetime.now(timezone.utc)
                ),
                explanation=f"Plan leaves residual risk score of {risk_score}."
            ))

        return evidence_list