import pytest
from app.infrastructure.integrations.models import DataSourceType, RecordStatus, IngestionStatus
from app.infrastructure.integrations.validators.quality_engine import DataQualityEngine
from app.infrastructure.integrations.normalizers.registry import NormalizerRegistry
from app.infrastructure.integrations.service import IngestionService

def test_quality_engine_valid():
    engine = DataQualityEngine()
    result = engine.validate(DataSourceType.TMS.value, {
        "tms_id": "TRN-999",
        "name": "Test",
        "desc": "Valid description"
    })
    assert result.status == RecordStatus.VALID
    assert result.checks_failed == 0

def test_quality_engine_missing_id():
    engine = DataQualityEngine()
    result = engine.validate(DataSourceType.TMS.value, {
        "name": "Missing ID",
        "desc": "Valid description"
    })
    assert result.status == RecordStatus.INVALID
    assert "Missing required field: tms_id" in result.errors

def test_quality_engine_warning():
    engine = DataQualityEngine()
    result = engine.validate(DataSourceType.TMS.value, {
        "tms_id": "TRN-999",
        "name": "Test"
    })
    assert result.status == RecordStatus.VALID_WITH_WARNINGS
    assert "Optional description is missing" in result.warnings

def test_smms_validation():
    engine = DataQualityEngine()
    result = engine.validate(DataSourceType.SMMS.value, {
        "smms_task_id": "TASK-1",
        "min_mins": 100,
        "max_mins": 50,
        "desc": "Invalid mins"
    })
    assert result.status == RecordStatus.INVALID
    assert "min_mins cannot be greater than max_mins" in result.errors

def test_normalizer_tms():
    registry = NormalizerRegistry()
    train = registry.normalize(DataSourceType.TMS, {
        "tms_id": "TRN-500",
        "name": "Express 500",
        "number": "500X",
        "train_type": "PASSENGER",
        "origin": "STN-A",
        "destination": "STN-B",
        "max_velocity_kmh": 120,
        "length_meters": 300,
        "weight_tons": 500,
        "priority_class": 1
    })
    assert train.service.train_id == "TRN-500"
    assert train.service.name == "Express 500"
    assert train.max_speed_kmh == 120

def test_ingestion_service_idempotency():
    service = IngestionService()
    
    # Run first time
    batch1 = service.run_ingestion(DataSourceType.TMS, "corr-1")
    assert batch1.status == IngestionStatus.COMPLETED
    assert batch1.record_count == 1
    assert batch1.accepted_count == 1
    assert batch1.duplicate_count == 0
    
    # Run second time - should be duplicate
    batch2 = service.run_ingestion(DataSourceType.TMS, "corr-2")
    assert batch2.status == IngestionStatus.COMPLETED
    assert batch2.record_count == 1
    assert batch2.duplicate_count == 1
    assert batch2.accepted_count == 0

def test_ingestion_service_quarantine():
    service = IngestionService()
    
    # Inject bad data into adapter
    bad_payload = {"name": "Bad Train"}  # Missing tms_id
    service.adapters[DataSourceType.TMS].fetch = lambda x: [bad_payload]
    
    batch = service.run_ingestion(DataSourceType.TMS, "corr-1")
    assert batch.rejected_count == 1
    assert batch.accepted_count == 0
    
    # Verify it's in quarantine
    assert len(service._quarantines) == 1
    q = list(service._quarantines.values())[0]
    assert q.source == DataSourceType.TMS
    assert "Missing required field: tms_id" in q.errors
