from typing import List, Dict, Any
from datetime import datetime, timezone
from app.domain.engine.forecasting.interfaces import HistoricalDataProvider
from app.domain.models.common import TimeInterval
from app.domain.enums import DataState

class MockHistoricalDataProvider(HistoricalDataProvider):
    """
    Provides mock historical data for forecasting purposes,
    isolated appropriately by DataState and scenario_id.
    """
    
    def get_train_demand_history(self, scope_id: str, interval: TimeInterval, data_state: str, scenario_id: str = None) -> List[Dict[str, Any]]:
        # Deterministic mock historical observations
        return [
            {"timestamp": interval.start, "value": 5.0, "source": "TMS", "data_state": data_state},
            {"timestamp": interval.start, "value": 4.0, "source": "TMS", "data_state": data_state},
        ]

    def get_maintenance_history(self, scope_id: str, interval: TimeInterval, data_state: str, scenario_id: str = None) -> List[Dict[str, Any]]:
        return [
            {"timestamp": interval.start, "value": 2.0, "source": "SMMS", "data_state": data_state},
        ]