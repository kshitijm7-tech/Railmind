import uuid
from typing import Dict, Any, List
from app.domain.models.risk import RiskPredictionRequest, RiskFactor, RiskLevel
from app.domain.engine.risk.interfaces import RiskPredictionEngine

class DeterministicBaselineRiskEngine(RiskPredictionEngine):
    model_name = "DeterministicHeuristicRisk"
    model_version = "1.0.0"

    def predict(
        self, 
        request: RiskPredictionRequest, 
        features: Dict[str, Any]
    ) -> Dict[str, Any]:
        factors = []
        total_score = 0.0
        
        # Define deterministic weights based on target_type
        # For simplicity, using a generalized weight set
        weights = {
            "defect_severity_score": 0.4,
            "asset_criticality_score": 0.3,
            "priority_score": 0.2,
            "forecast_pressure_score": 0.1
        }
        
        # Calculate scores & build factors
        for f_key, weight in weights.items():
            raw_val = features.get(f_key, 0.0)
            contribution = raw_val * weight
            total_score += contribution
            
            if raw_val > 0:
                factors.append(RiskFactor(
                    factor_id=f"FCT-{uuid.uuid4().hex[:6]}",
                    factor_type=f_key.upper(),
                    raw_value=raw_val,
                    normalized_value=raw_val,
                    weight=weight,
                    contribution=contribution,
                    direction=1,
                    explanation=f"{f_key.replace('_score', '')} contributes {contribution:.1f} to total risk."
                ))
                
        # Cap score at 100
        final_score = min(100.0, max(0.0, total_score))
        
        # Determine Level
        if final_score >= 75:
            level = RiskLevel.CRITICAL
        elif final_score >= 50:
            level = RiskLevel.HIGH
        elif final_score >= 25:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW
            
        # Build Explanation
        if len(factors) == 0:
            exp = "Risk is LOW because no significant risk factors were detected."
        else:
            top_factor = sorted(factors, key=lambda x: x.contribution, reverse=True)[0]
            exp = f"{request.target_type.value} risk is {level.value} driven primarily by {top_factor.factor_type.lower()}."

        return {
            "risk_score": final_score,
            "risk_level": level,
            "probability": None,  # Explicitly NOT a probability
            "impact": None,
            "factors": factors,
            "explanation": exp
        }