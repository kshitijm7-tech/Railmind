from typing import Protocol, List, Dict, Any
from datetime import datetime
from app.domain.models.forecasting import ForecastRequest, ForecastObservation, ForecastQuality
from app.domain.models.common import TimeInterval

class HistoricalDataProvider(Protocol):
    def get_train_demand_history(self, scope_id: str, interval: TimeInterval, data_state: str, scenario_id: str = None) -> List[Dict[str, Any]]:
        ...

    def get_maintenance_history(self, scope_id: str, interval: TimeInterval, data_state: str, scenario_id: str = None) -> List[Dict[str, Any]]:
        ...

class FeatureExtractor(Protocol):
    def extract_features(self, request: ForecastRequest, raw_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extracts features, ensuring strictly no data >= request.horizon.start is used."""
        ...

class ForecastEngine(Protocol):
    model_name: str
    model_version: str
    
    def forecast(self, request: ForecastRequest, features: Dict[str, Any]) -> List[ForecastObservation]:
        ...