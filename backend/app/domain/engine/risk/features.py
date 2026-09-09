from typing import Dict, Any
from datetime import datetime
from app.domain.models.risk import RiskPredictionRequest
from app.domain.engine.risk.interfaces import RiskFeatureBuilder

class StandardRiskFeatureBuilder(RiskFeatureBuilder):
    feature_version = "1.0.0"

    def build_features(
        self, 
        request: RiskPredictionRequest, 
        raw_context: Dict[str, Any],
        priority_context: Dict[str, Any],
        forecast_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        cutoff_time = request.requested_at
        
        features = {
            "defect_severity_score": 0.0,
            "asset_criticality_score": 0.0,
            "forecast_pressure_score": 0.0,
            "priority_score": 0.0,
            "valid_evidence_count": 0
        }
        
        # 1. Evaluate Raw Context (Assets/Defects)
        defects = raw_context.get("defects", [])
        for defect in defects:
            if defect.get("timestamp") and defect["timestamp"] >= cutoff_time:
                continue # Temporal leakage protection
            severity = defect.get("severity", "MINOR")
            val = {"CRITICAL": 100, "SEVERE": 75, "MODERATE": 50, "MINOR": 25}.get(severity, 0)
            features["defect_severity_score"] = max(features["defect_severity_score"], val)
            features["valid_evidence_count"] += 1
            
        assets = raw_context.get("assets", [])
        for asset in assets:
            if asset.get("timestamp") and asset["timestamp"] >= cutoff_time:
                continue
            cond = asset.get("condition", "GOOD")
            val = {"DEGRADED": 100, "FAIR": 50, "GOOD": 0}.get(cond, 0)
            features["asset_criticality_score"] = max(features["asset_criticality_score"], val)
            features["valid_evidence_count"] += 1
            
        # 2. Evaluate P10 Context
        if priority_context:
            priority_ts = priority_context.get("timestamp")
            if not priority_ts or priority_ts < cutoff_time:
                # We normalize P10 priority class into a risk contributor
                p_class = priority_context.get("priority_class", "LOW")
                features["priority_score"] = {"CRITICAL": 100, "HIGH": 75, "MEDIUM": 50, "LOW": 25}.get(p_class, 0)
                features["valid_evidence_count"] += 1

        # 3. Evaluate P15 Forecast Context
        if forecast_context:
            # We ONLY consider forecast data if it was generated before the cutoff
            forecast_gen = forecast_context.get("generated_at")
            if forecast_gen and forecast_gen < cutoff_time:
                # E.g. pressure forecast for the horizon
                features["forecast_pressure_score"] = forecast_context.get("pressure_value", 0.0)
                features["valid_evidence_count"] += 1
                
        return features