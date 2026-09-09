from typing import Dict, Any, List
from datetime import datetime
from app.domain.models.forecasting import ForecastRequest
from app.domain.engine.forecasting.interfaces import FeatureExtractor

class TimeSeriesFeatureExtractor(FeatureExtractor):
    feature_version = "1.0.0"

    def extract_features(self, request: ForecastRequest, raw_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        cutoff_time = request.horizon.start
        
        # Enforce temporal leakage protection
        valid_history = []
        for record in raw_history:
            record_time = record.get("timestamp")
            if not record_time:
                continue
            if record_time >= cutoff_time:
                # Discard future data to prevent leakage
                continue
            valid_history.append(record)
            
        # Group by buckets (simple implementation for baseline)
        return {
            "valid_history": valid_history,
            "count": len(valid_history)
        }