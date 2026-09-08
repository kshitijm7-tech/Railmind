import pytest
from datetime import datetime, timedelta, timezone
from app.domain.models.risk import RiskPredictionRequest, RiskType, RiskLevel, RiskQualityLevel
from app.domain.models.common import TimeInterval
from app.domain.enums import DataState
from app.domain.engine.risk.features import StandardRiskFeatureBuilder
from app.domain.engine.risk.baseline import DeterministicBaselineRiskEngine
from app.application.services.risk_service import RiskPredictionService

def test_temporal_leakage_protection():
    builder = StandardRiskFeatureBuilder()
    now = datetime.now(timezone.utc)
    
    request = RiskPredictionRequest(
        request_id="REQ-1",
        target_type=RiskType.ASSET_FAILURE,
        target_id="AST-1",
        horizon=TimeInterval(start=now, end=now + timedelta(hours=1)),
        requested_at=now
    )
    
    raw_context = {
        "defects": [
            {"severity": "CRITICAL", "timestamp": now - timedelta(hours=2)}, # Valid
            {"severity": "CRITICAL", "timestamp": now + timedelta(hours=2)}, # LEAKAGE (future)
        ],
        "assets": [
            {"condition": "DEGRADED", "timestamp": now - timedelta(minutes=5)} # Valid
        ]
    }
    
    features = builder.build_features(request, raw_context, {}, {})
    # Only 2 valid evidences (1 past defect, 1 past asset)
    assert features["valid_evidence_count"] == 2
    assert features["defect_severity_score"] == 100 # From the valid defect

def test_risk_baseline_engine():
    engine = DeterministicBaselineRiskEngine()
    now = datetime.now(timezone.utc)
    
    request = RiskPredictionRequest(
        request_id="REQ-1",
        target_type=RiskType.ASSET_FAILURE,
        target_id="AST-1",
        horizon=TimeInterval(start=now, end=now + timedelta(hours=1)),
        requested_at=now
    )
    
    features = {
        "defect_severity_score": 100, # Weight 0.4 -> 40
        "asset_criticality_score": 100, # Weight 0.3 -> 30
        "priority_score": 50, # Weight 0.2 -> 10
        "forecast_pressure_score": 0 # Weight 0.1 -> 0
    }
    
    result = engine.predict(request, features)
    assert result["risk_score"] == 80.0
    assert result["risk_level"] == RiskLevel.CRITICAL
    assert len(result["factors"]) == 3
    assert result["probability"] is None

def test_risk_service_insufficient_data():
    service = RiskPredictionService()
    now = datetime.now(timezone.utc)
    
    request = RiskPredictionRequest(
        request_id="REQ-1",
        target_type=RiskType.ASSET_FAILURE,
        target_id="AST-1",
        horizon=TimeInterval(start=now, end=now + timedelta(hours=1)),
        requested_at=now
    )
    
    result = service.generate_prediction(request, {}, {}, {})
    
    assert result.risk_level == RiskLevel.LOW
    assert result.quality.level == RiskQualityLevel.INSUFFICIENT
    assert result.risk_score == 0.0

def test_scenario_isolation_in_provenance():
    service = RiskPredictionService()
    now = datetime.now(timezone.utc)
    
    request = RiskPredictionRequest(
        request_id="REQ-1",
        target_type=RiskType.ASSET_FAILURE,
        target_id="AST-1",
        horizon=TimeInterval(start=now, end=now + timedelta(hours=1)),
        state_mode=DataState.MOCKED,
        requested_at=now
    )
    
    result = service.generate_prediction(request, {}, {}, {})
    assert result.provenance.state == DataState.MOCKED
