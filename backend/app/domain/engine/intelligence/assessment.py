from typing import Dict, Any, List
from app.domain.models.intelligence import (
    DecisionIntelligenceRequest, CandidateAssessment, DecisionEvidence, DecisionTradeoff
)
from app.domain.engine.intelligence.interfaces import DecisionAssessmentEngine

class DeterministicDecisionAssessmentEngine(DecisionAssessmentEngine):
    engine_name = "DeterministicHeuristicDecision"
    engine_version = "1.0.0"
    feature_version = "1.0.0"

    def assess_candidates(
        self,
        request: DecisionIntelligenceRequest,
        evidence: List[DecisionEvidence]
    ) -> Dict[str, Any]:
        
        candidates_map: Dict[str, Dict[str, Any]] = {
            pid: {"score": 0.0, "strengths": [], "weaknesses": [], "evidence_ids": [], "tradeoffs": []}
            for pid in request.candidate_plan_ids
        }
        
        # 1. Aggregate Scores from Evidence
        for ev in evidence:
            plan_id = None
            # Extract plan_id from source_reference e.g., SIM_plan123
            if "_" in ev.source_reference:
                parts = ev.source_reference.split("_")
                plan_id = parts[-1]
                
            if plan_id and plan_id in candidates_map:
                # Direction: 1 (positive), -1 (negative)
                # We normalize the evidence summary value based on its type.
                # Delay minutes might be up to 1000, completed tasks up to 100, risk up to 100
                if ev.evidence_type.value == "SIMULATION":
                    if ev.direction == -1:
                        # e.g., 1 delay min = -0.1 score
                        impact = ev.summary_value * 0.1
                        candidates_map[plan_id]["score"] -= impact
                        if ev.severity == "HIGH":
                            candidates_map[plan_id]["weaknesses"].append(ev.explanation)
                    else:
                        # e.g., 1 task completed = +5 score
                        impact = ev.summary_value * 5.0
                        candidates_map[plan_id]["score"] += impact
                        if ev.severity == "HIGH":
                            candidates_map[plan_id]["strengths"].append(ev.explanation)
                
                elif ev.evidence_type.value == "RISK":
                    impact = ev.summary_value * 0.5 # 100 risk = -50 score
                    candidates_map[plan_id]["score"] -= impact
                    if ev.severity in ["HIGH", "CRITICAL"]:
                        candidates_map[plan_id]["weaknesses"].append(ev.explanation)
                        
                candidates_map[plan_id]["evidence_ids"].append(ev.evidence_id)

        # 2. Build CandidateAssessments
        assessments: List[CandidateAssessment] = []
        for pid, data in candidates_map.items():
            assessments.append(CandidateAssessment(
                plan_id=pid,
                rank=0, # Will sort later
                score=data["score"],
                strengths=list(set(data["strengths"])),
                weaknesses=list(set(data["weaknesses"])),
                tradeoffs=[],
                evidence_ids=data["evidence_ids"]
            ))
            
        # 3. Sort and Rank deterministically
        # Sort by score DESC, then by plan_id ASC to ensure stable tie-breaking
        assessments.sort(key=lambda x: (-x.score, x.plan_id))
        
        for i, assessment in enumerate(assessments):
            assessment.rank = i + 1
            
        # 4. Generate Tradeoffs and Explanations
        recommended_id = None
        overall_exp = "No candidates available for assessment."
        primary_drivers = []
        
        # Check if there is any evidence at all
        has_evidence = any(len(a.evidence_ids) > 0 for a in assessments)
        
        if assessments:
            if not has_evidence:
                # INSUFFICIENT EVIDENCE
                overall_exp = "Insufficient evidence to make a recommendation. All candidates have zero evidence score."
            else:
                # SUPPORTED RECOMMENDATION
                recommended_id = assessments[0].plan_id
                if len(assessments) > 1:
                    top = assessments[0]
                    alt = assessments[1]
                    delta = top.score - alt.score
                    if delta == 0:
                        overall_exp = f"Candidate {top.plan_id} is recommended over {alt.plan_id} based on tie-breaking rules, as both present equivalent evidence scores."
                    else:
                        overall_exp = f"Candidate {top.plan_id} is recommended. It scores higher by {delta:.1f} compared to the next best alternative ({alt.plan_id})."
                    
                    # Assign comparative tradeoffs
                    top.tradeoffs.append(DecisionTradeoff(
                        factor_name="Score Advantage",
                        description=f"Outperforms alternative {alt.plan_id} by {delta:.1f} points.",
                        is_strength=True
                    ))
                    alt.tradeoffs.append(DecisionTradeoff(
                        factor_name="Score Disadvantage",
                        description=f"Underperforms recommended plan {top.plan_id} by {delta:.1f} points.",
                        is_strength=False
                    ))
                else:
                    overall_exp = f"Candidate {assessments[0].plan_id} is recommended as it is the only viable candidate evaluated."
                    
                if assessments[0].strengths:
                    primary_drivers.extend(assessments[0].strengths)

        return {
            "recommended_plan_id": recommended_id,
            "candidates": assessments,
            "primary_drivers": primary_drivers,
            "overall_explanation": overall_exp
        }