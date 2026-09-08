import pytest
from datetime import datetime, timedelta, timezone
from app.domain.models.forecasting import ForecastRequest, ForecastTargetType, ForecastScope, ForecastQualityLevel
from app.domain.models.common import TimeInterval
from app.domain.enums import DataState
from app.domain.engine.forecasting.features import TimeSeriesFeatureExtractor
from app.domain.engine.forecasting.baseline import DeterministicBaselineForecaster
from app.domain.engine.forecasting.evaluation import calculate_mae, calculate_mape, calculate_rmse
from app.application.services.forecasting_service import ForecastingService

def test_feature_extractor_prevents_temporal_leakage():
    extractor = TimeSeriesFeatureExtractor()
    now = datetime.now(timezone.utc)
    
    request = ForecastRequest(
        request_id="REQ-1",
        target_type=ForecastTargetType.TRAIN_DEMAND,
        scope=ForecastScope.SECTION,
        horizon=TimeInterval(start=now, end=now + timedelta(hours=1)),
        granularity_minutes=15,
        requested_at=now
    )
    
    raw_history = [
        {"timestamp": now - timedelta(hours=2), "value": 10}, # Valid historical
        {"timestamp": now + timedelta(minutes=10), "value": 20}, # FUTURE LEAKAGE!
    ]
    
    features = extractor.extract_features(request, raw_history)
    
    assert features["count"] == 1
    assert features["valid_history"][0]["value"] == 10

def test_baseline_forecaster():
    engine = DeterministicBaselineForecaster()
    now = datetime.now(timezone.utc)
    
    request = ForecastRequest(
        request_id="REQ-1",
        target_type=ForecastTargetType.TRAIN_DEMAND,
        scope=ForecastScope.SECTION,
        horizon=TimeInterval(start=now, end=now + timedelta(hours=1)),
        granularity_minutes=30,
        requested_at=now
    )
    
    features = {
        "valid_history": [
            {"value": 10.0},
            {"value": 20.0}
        ],
        "count": 2
    }
    
    obs = engine.forecast(request, features)
    assert len(obs) == 2 # 1 hour at 30 min granularity
    assert obs[0].predicted_value == 15.0 # (10 + 20) / 2
    assert obs[1].predicted_value == 15.0

def test_evaluation_metrics():
    actuals = [10.0, 20.0, 30.0]
    preds = [12.0, 18.0, 30.0]
    
    mae = calculate_mae(actuals, preds)
    assert mae == 4.0 / 3.0
    
    mape = calculate_mape(actuals, preds)
    # errs: 2/10 (0.2), 2/20 (0.1), 0/30 (0) -> (0.3 / 3) * 100 = 10%
    assert abs(mape - 10.0) < 0.001

def test_service_insufficient_data():
    service = ForecastingService()
    now = datetime.now(timezone.utc)
    
    request = ForecastRequest(
        request_id="REQ-1",
        target_type=ForecastTargetType.TRAIN_DEMAND,
        scope=ForecastScope.SECTION,
        horizon=TimeInterval(start=now, end=now + timedelta(hours=1)),
        granularity_minutes=30,
        requested_at=now
    )
    
    # Force empty history
    service.historical_provider.get_train_demand_history = lambda *args: []
    
    result = service.generate_forecast(request)
    assert result.quality.level == ForecastQualityLevel.INSUFFICIENT
    assert result.predictions[0].predicted_value == 0.0
    assert result.predictions[0].confidence == 0.0