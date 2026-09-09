import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.domain.models.forecasting import (
    ForecastRequest, ForecastResult, ForecastQuality, ForecastQualityLevel, ForecastTargetType
)
from app.domain.models.common import Provenance, TimeInterval
from app.domain.engine.forecasting.features import TimeSeriesFeatureExtractor
from app.domain.engine.forecasting.baseline import DeterministicBaselineForecaster
from app.infrastructure.forecasting.historical_provider import MockHistoricalDataProvider

class ForecastingService:
    def __init__(self):
        self.feature_extractor = TimeSeriesFeatureExtractor()
        self.engine = DeterministicBaselineForecaster()
        self.historical_provider = MockHistoricalDataProvider()
        
    def generate_forecast(self, request: ForecastRequest) -> ForecastResult:
        # Determine history window
        # Mock logic: assume we look back 30 days
        history_start = request.horizon.start.replace(day=1) # simplified
        history_interval = TimeInterval(start=history_start, end=request.horizon.start)
        
        # 1. Fetch History
        if request.target_type == ForecastTargetType.TRAIN_DEMAND:
            raw_history = self.historical_provider.get_train_demand_history(
                request.scope_id or "ALL", history_interval, request.state_mode, request.scenario_id
            )
        else:
            raw_history = self.historical_provider.get_maintenance_history(
                request.scope_id or "ALL", history_interval, request.state_mode, request.scenario_id
            )
            
        # 2. Extract Features
        features = self.feature_extractor.extract_features(request, raw_history)
        valid_count = features.get("count", 0)
        
        # 3. Data Quality Gate
        if valid_count == 0:
            quality = ForecastQuality(
                score=0.0,
                level=ForecastQualityLevel.INSUFFICIENT,
                warnings=["Insufficient historical data to produce a reliable forecast."]
            )
        elif valid_count < 5:
            quality = ForecastQuality(
                score=0.5,
                level=ForecastQualityLevel.LOW,
                warnings=["Low volume of historical data."]
            )
        else:
            quality = ForecastQuality(
                score=0.9,
                level=ForecastQualityLevel.HIGH,
                dimensions={"completeness": 1.0, "freshness": 1.0}
            )
            
        # 4. Engine execution
        observations = self.engine.forecast(request, features)
        
        from app.domain.enums import DataSource
        provenance = Provenance(
            state=request.state_mode,
            source=DataSource.SYSTEM,
            generatedAt=datetime.now(timezone.utc),
            generatorVersion="1.0.0"
        )
        
        explanation = f"Forecast generated using a deterministic rolling baseline. " \
                      f"Confidence is {quality.level.value} based on {valid_count} historical observations."
        
        return ForecastResult(
            forecast_id=f"FCST-{uuid.uuid4().hex[:8]}",
            request=request,
            predictions=observations,
            model_name=self.engine.model_name,
            model_version=self.engine.model_version,
            feature_version=self.feature_extractor.feature_version,
            engine_version="1.0.0",
            quality=quality,
            provenance=provenance,
            explanation=explanation,
            historical_window=history_interval,
            generated_at=datetime.now(timezone.utc)
        )