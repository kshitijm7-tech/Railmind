import pytest
from datetime import datetime, timedelta, timezone
from app.domain.models.recovery import (
    Disruption, DisruptionType, DisruptionSeverity, DisruptionStatus, 
    RecoveryAssessmentRequest
)
from app.domain.models.common import Provenance
from app.domain.enums import DataState, DataSource
from app.application.services.recovery_service import RecoveryService

def test_recovery_impact_assessment():
    service = RecoveryService()
    now = datetime.now(timezone.utc)
    
    prov = Provenance(
        state=DataState.LIVE,
        source=DataSource.SYSTEM,
        generatedAt=now,
        generatorVersion="1.0"
    )
    
    disruption = Disruption(
        disruption_id="DIS-1",
        type=DisruptionType.TRACK_FAILURE,
        severity=DisruptionSeverity.MAJOR,
        status=DisruptionStatus.ACTIVE,
        affected_resource="SEC-100",
        affected_resource_type="SECTION",
        start_time=now - timedelta(hours=1),
        expected_end_time=now + timedelta(hours=5),
        description="Major track failure on SEC-100",
        state_mode=DataState.LIVE,
        reported_at=now - timedelta(hours=1),
        source="SCADA",
        provenance=prov
    )
    
    request = RecoveryAssessmentRequest(
        request_id="REQ-1",
        disruption=disruption,
        base_plan_id="PLAN-A",
        requested_at=now
    )
    
    raw_context = {
        "blocks": [{"block_id": "BLK-1", "section_id": "SEC-100", "tasks": ["TSK-1"]}],
        "train_paths": [{"train_id": "TRN-1", "segments": [{"section_id": "SEC-100"}]}]
    }
    
    result = service.assess_recovery(request, raw_context)
    
    assert result.impact_assessment.disruption_id == "DIS-1"
    assert "TRN-1" in result.impact_assessment.affected_trains
    assert "BLK-1" in result.impact_assessment.affected_blocks
    assert "TSK-1" in result.impact_assessment.affected_maintenance_tasks
    assert result.impact_assessment.delay_exposure_minutes == 30.0
    
    # Check that candidates are generated
    assert len(result.recovery_options) > 1 # NO_ACTION + SHIFT_BLOCK + CANCEL_MAINT
    
    # 1 option should be NO_ACTION
    no_actions = [o for o in result.recovery_options if o.actions[0].action_type.value == "NO_ACTION"]
    assert len(no_actions) == 1
    
    # Quality should be MEDIUM because P09 constraints were not validated
    assert result.quality == "MEDIUM"

def test_recovery_temporal_leakage():
    service = RecoveryService()
    now = datetime.now(timezone.utc)
    
    prov = Provenance(
        state=DataState.LIVE,
        source=DataSource.SYSTEM,
        generatedAt=now,
        generatorVersion="1.0"
    )
    
    # Disruption start_time is in the future relative to requested_at
    disruption = Disruption(
        disruption_id="DIS-1",
        type=DisruptionType.TRACK_FAILURE,
        severity=DisruptionSeverity.MAJOR,
        status=DisruptionStatus.ACTIVE,
        affected_resource="SEC-100",
        affected_resource_type="SECTION",
        start_time=now + timedelta(hours=1), # Future
        expected_end_time=now + timedelta(hours=5),
        description="Major track failure on SEC-100",
        state_mode=DataState.LIVE,
        reported_at=now,
        source="SCADA",
        provenance=prov
    )
    
    request = RecoveryAssessmentRequest(
        request_id="REQ-1",
        disruption=disruption,
        base_plan_id="PLAN-A",
        requested_at=now
    )
    
    with pytest.raises(ValueError, match="Cannot assess future disruption"):
        service.assess_recovery(request, {})

def test_recovery_scenario_isolation():
    service = RecoveryService()
    now = datetime.now(timezone.utc)
    
    prov = Provenance(
        state=DataState.MOCKED,
        source=DataSource.SYSTEM,
        generatedAt=now,
        generatorVersion="1.0"
    )
    
    disruption = Disruption(
        disruption_id="DIS-1",
        type=DisruptionType.TRACK_FAILURE,
        severity=DisruptionSeverity.MAJOR,
        status=DisruptionStatus.ACTIVE,
        affected_resource="SEC-100",
        affected_resource_type="SECTION",
        start_time=now - timedelta(hours=1),
        expected_end_time=now + timedelta(hours=5),
        description="Major track failure on SEC-100",
        state_mode=DataState.MOCKED,
        reported_at=now,
        source="SCADA",
        provenance=prov
    )
    
    request = RecoveryAssessmentRequest(
        request_id="REQ-1",
        disruption=disruption,
        base_plan_id="PLAN-A",
        requested_at=now
    )
    
    # Pass LIVE context intentionally expecting rejection
    with pytest.raises(ValueError, match="State mode mismatch"):
        service.assess_recovery(request, {"expected_state_mode": DataState.LIVE})