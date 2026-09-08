from typing import Protocol, List, Dict, Any
from app.domain.models.risk import RiskPredictionRequest, RiskFactor, RiskLevel
from app.domain.models.common import TimeInterval

class RiskFeatureBuilder(Protocol):
    feature_version: str
    
    def build_features(
        self, 
        request: RiskPredictionRequest, 
        raw_context: Dict[str, Any],
        priority_context: Dict[str, Any],
        forecast_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Builds risk features while enforcing temporal constraints and isolation rules."""
        ...

class RiskPredictionEngine(Protocol):
    model_name: str
    model_version: str
    
    def predict(
        self, 
        request: RiskPredictionRequest, 
        features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Returns a dict containing:
        - risk_score: float (0-100)
        - risk_level: RiskLevel
        - probability: Optional[float]
        - impact: Optional[float]
        - factors: List[RiskFactor]
        - explanation: str
        """
        ...