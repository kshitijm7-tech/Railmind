from typing import Dict, Any, List
from datetime import timedelta
from app.domain.models.forecasting import ForecastRequest, ForecastObservation
from app.domain.engine.forecasting.interfaces import ForecastEngine

class DeterministicBaselineForecaster(ForecastEngine):
    model_name = "DeterministicRollingAverage"
    model_version = "1.0.0"

    def forecast(self, request: ForecastRequest, features: Dict[str, Any]) -> List[ForecastObservation]:
        history = features.get("valid_history", [])
        
        # Super simple moving average or hourly average based on history
        # For simplicity, if we have counts per hour in history, we average them.
        
        # Compute baseline average (value per minute/hour whatever)
        total_value = sum(r.get("value", 1.0) for r in history)
        avg_val = total_value / max(1, len(history)) if history else 0.0
        
        observations = []
        current_time = request.horizon.start
        
        while current_time < request.horizon.end:
            obs = ForecastObservation(
                timestamp=current_time,
                predicted_value=avg_val,
                lower_bound=max(0.0, avg_val * 0.8),
                upper_bound=avg_val * 1.2,
                confidence=0.7 if history else 0.0
            )
            observations.append(obs)
            current_time += timedelta(minutes=request.granularity_minutes)
            
        return observations