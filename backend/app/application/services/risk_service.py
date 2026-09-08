import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.domain.models.risk import (
    RiskPredictionRequest, RiskPredictionResult, RiskQuality, RiskQualityLevel, RiskLevel
)
from app.domain.models.common import Provenance
from app.domain.engine.risk.features import StandardRiskFeatureBuilder
from app.domain.engine.risk.baseline import DeterministicBaselineRiskEngine
from app.domain.enums import DataSource

class RiskPredictionService:
    def __init__(self):
        self.feature_builder = StandardRiskFeatureBuilder()
        self.engine = DeterministicBaselineRiskEngine()
        
    def generate_prediction(self, request: RiskPredictionRequest, raw_context: Dict[str, Any], priority_context: Dict[str, Any], forecast_context: Dict[str, Any]) -> RiskPredictionResult:
        
        # 1. Feature Building
        features = self.feature_builder.build_features(request, raw_context, priority_context, forecast_context)
        valid_evidence_count = features.get("valid_evidence_count", 0)
        
        # 2. Risk Quality Gate
        if valid_evidence_count == 0:
            quality = RiskQuality(
                level=RiskQualityLevel.INSUFFICIENT,
                warnings=["Insufficient evidence to calculate risk."]
            )
            # Short-circuit logic for insufficient data
            return self._build_empty_result(request, quality)
            
        elif valid_evidence_count < 2:
            quality = RiskQuality(
                level=RiskQualityLevel.LOW,
                warnings=["Low volume of risk evidence."]
            )
        else:
            quality = RiskQuality(
                level=RiskQualityLevel.HIGH,
                dimensions={"evidence_count": valid_evidence_count}
            )
            
        # 3. Engine execution
        prediction = self.engine.predict(request, features)
        
        # 4. Provenance
        provenance = Provenance(
            state=request.state_mode,
            source=DataSource.SYSTEM,
            generatedAt=datetime.now(timezone.utc),
            generatorVersion="1.0.0"
        )
        
        return RiskPredictionResult(
            risk_id=f"RSK-{uuid.uuid4().hex[:8]}",
            request=request,
            risk_level=prediction["risk_level"],
            risk_score=prediction["risk_score"],
            probability=prediction["probability"],
            impact=prediction["impact"],
            factors=prediction["factors"],
            explanation=prediction["explanation"],
            quality=quality,
            provenance=provenance,
            model_name=self.engine.model_name,
            model_version=self.engine.model_version,
            feature_version=self.feature_builder.feature_version,
            engine_version="1.0.0",
            generated_at=datetime.now(timezone.utc)
        )
        
    def _build_empty_result(self, request: RiskPredictionRequest, quality: RiskQuality) -> RiskPredictionResult:
        provenance = Provenance(
            state=request.state_mode,
            source=DataSource.SYSTEM,
            generatedAt=datetime.now(timezone.utc),
            generatorVersion="1.0.0"
        )
        return RiskPredictionResult(
            risk_id=f"RSK-{uuid.uuid4().hex[:8]}",
            request=request,
            risk_level=RiskLevel.LOW,
            risk_score=0.0,
            probability=None,
            impact=None,
            factors=[],
            explanation="Insufficient evidence to predict risk. Defaulting to LOW.",
            quality=quality,
            provenance=provenance,
            model_name=self.engine.model_name,
            model_version=self.engine.model_version,
            feature_version=self.feature_builder.feature_version,
            engine_version="1.0.0",
            generated_at=datetime.now(timezone.utc)
        )