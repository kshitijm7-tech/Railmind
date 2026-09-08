"""
P10 Priority Engine Tests
=========================
Tests cover:
  - Individual factor behavior
  - Priority class thresholds
  - Combined factor scenarios
  - Determinism
  - Missing-data behavior (no defect)
  - API endpoint integration
"""
import pytest
from datetime import datetime, timezone
from app.domain.engine.priority_engine import DeterministicPriorityEngine, ENGINE_VERSION
from app.domain.engine.priority_models import PriorityClass
from app.domain.models.maintenance import MaintenanceTask, Defect, PriorityBreakdown, DurationMinutes
from app.domain.models.common import DurationMinutes as DM, Provenance
from app.domain.enums import (
    Criticality, TaskType, TaskStatus, Department,
    DefectSeverity, DefectStatus, DefectSource, DataState, DataSource,
)

engine = DeterministicPriorityEngine()


# ─── Fixtures ────────────────────────────────────────────────────────────────

def make_task(
    criticality=Criticality.HIGH,
    task_type=TaskType.CORRECTIVE,
    expected_minutes=60,
    task_id="TASK-TEST",
) -> MaintenanceTask:
    return MaintenanceTask(
        task_id=task_id,
        asset_id="AST-TEST",
        section_id="SEC-TEST",
        type=task_type,
        status=TaskStatus.PENDING,
        criticality=criticality,
        department=Department.TRACK,
        description="Test task",
        duration=DM(expected=expected_minutes, minimum=30, maximum=120),
        requires_power_block=False,
        requires_traffic_block=False,
    )


def make_defect(
    severity=DefectSeverity.SEVERE,
    criticality=Criticality.HIGH,
    is_safety_critical=False,
    urgency_hours=24,
) -> Defect:
    return Defect(
        defect_id="DEF-TEST",
        asset_id="AST-TEST",
        section_id="SEC-TEST",
        defect_type="CRACK",
        description="Test defect",
        severity=severity,
        criticality=criticality,
        detected_at=datetime.now(timezone.utc),
        detected_by=DefectSource.INSPECTION,
        operational_impact="Low",
        is_safety_critical=is_safety_critical,
        urgency_hours=urgency_hours,
        status=DefectStatus.ASSESSED,
        department=Department.TRACK,
        provenance=Provenance(state=DataState.MOCKED, source=DataSource.MOCK_GENERATOR, generatedAt=datetime.now(timezone.utc)),
    )


# ─── Criticality factor ───────────────────────────────────────────────────────

def test_critical_task_scores_higher_than_low():
    t_critical = make_task(criticality=Criticality.CRITICAL)
    t_low      = make_task(criticality=Criticality.LOW)
    r_critical = engine.evaluate(t_critical)
    r_low      = engine.evaluate(t_low)
    assert r_critical.score > r_low.score


def test_criticality_factor_present_in_result():
    task = make_task(criticality=Criticality.CRITICAL)
    result = engine.evaluate(task)
    factor_ids = [f.factor_id for f in result.factors]
    assert "criticality" in factor_ids


# ─── Defect severity factor ───────────────────────────────────────────────────

def test_critical_defect_higher_than_minor():
    task = make_task()
    d_critical = make_defect(severity=DefectSeverity.CRITICAL)
    d_minor    = make_defect(severity=DefectSeverity.MINOR)
    r_c = engine.evaluate(task, defect=d_critical)
    r_m = engine.evaluate(task, defect=d_minor)
    assert r_c.score > r_m.score


def test_no_defect_severity_zero_contribution():
    task = make_task()
    result = engine.evaluate(task, defect=None)
    sev_factor = next(f for f in result.factors if f.factor_id == "defect_severity")
    assert sev_factor.contribution == 0.0


# ─── Safety factor ────────────────────────────────────────────────────────────

def test_safety_critical_increases_score():
    task = make_task()
    d_safe    = make_defect(is_safety_critical=False)
    d_unsafe  = make_defect(is_safety_critical=True)
    r_safe   = engine.evaluate(task, defect=d_safe)
    r_unsafe = engine.evaluate(task, defect=d_unsafe)
    assert r_unsafe.score > r_safe.score


def test_safety_factor_max_when_critical():
    task = make_task()
    defect = make_defect(is_safety_critical=True)
    result = engine.evaluate(task, defect=defect)
    s_factor = next(f for f in result.factors if f.factor_id == "safety_critical")
    assert s_factor.normalized_value == 1.0


# ─── Urgency factor ───────────────────────────────────────────────────────────

def test_urgent_2h_scores_higher_than_48h():
    task = make_task()
    d_urgent = make_defect(urgency_hours=2)
    d_low    = make_defect(urgency_hours=48)
    r_u = engine.evaluate(task, defect=d_urgent)
    r_l = engine.evaluate(task, defect=d_low)
    assert r_u.score > r_l.score


def test_urgency_zero_hours_max_contribution():
    task   = make_task()
    defect = make_defect(urgency_hours=0)
    result = engine.evaluate(task, defect=defect)
    u_factor = next(f for f in result.factors if f.factor_id == "urgency")
    assert u_factor.normalized_value == 1.0


def test_urgency_72h_zero_contribution():
    task   = make_task()
    defect = make_defect(urgency_hours=72)
    result = engine.evaluate(task, defect=defect)
    u_factor = next(f for f in result.factors if f.factor_id == "urgency")
    assert u_factor.normalized_value == 0.0


# ─── Train impact factor ──────────────────────────────────────────────────────

def test_more_train_impacts_raise_score():
    task = make_task()
    r_high = engine.evaluate(task, num_train_impacts=5)
    r_low  = engine.evaluate(task, num_train_impacts=0)
    assert r_high.score > r_low.score


def test_zero_train_impacts_zero_contribution():
    task   = make_task()
    result = engine.evaluate(task, num_train_impacts=0)
    t_factor = next(f for f in result.factors if f.factor_id == "train_impact")
    assert t_factor.contribution == 0.0


# ─── Task type factor ─────────────────────────────────────────────────────────

def test_emergency_type_higher_than_inspection():
    t_emergency  = make_task(task_type=TaskType.EMERGENCY)
    t_inspection = make_task(task_type=TaskType.INSPECTION)
    r_em = engine.evaluate(t_emergency)
    r_in = engine.evaluate(t_inspection)
    assert r_em.score > r_in.score


# ─── Duration factor ──────────────────────────────────────────────────────────

def test_longer_duration_higher_disruption():
    t_long  = make_task(expected_minutes=480)
    t_short = make_task(expected_minutes=30)
    r_long  = engine.evaluate(t_long)
    r_short = engine.evaluate(t_short)
    assert r_long.score > r_short.score


# ─── Priority classes ─────────────────────────────────────────────────────────

def test_max_inputs_yield_critical_class():
    task   = make_task(criticality=Criticality.CRITICAL, task_type=TaskType.EMERGENCY, expected_minutes=480)
    defect = make_defect(severity=DefectSeverity.CRITICAL, criticality=Criticality.CRITICAL,
                         is_safety_critical=True, urgency_hours=0)
    result = engine.evaluate(task, defect=defect, num_train_impacts=5)
    assert result.priority_class == PriorityClass.CRITICAL


def test_min_inputs_yield_low_class():
    task   = make_task(criticality=Criticality.LOW, task_type=TaskType.INSPECTION, expected_minutes=10)
    result = engine.evaluate(task, defect=None, num_train_impacts=0)
    assert result.priority_class == PriorityClass.LOW


# ─── Determinism ─────────────────────────────────────────────────────────────

def test_same_input_same_result():
    task   = make_task(criticality=Criticality.HIGH)
    defect = make_defect(severity=DefectSeverity.SEVERE, urgency_hours=12)
    r1 = engine.evaluate(task, defect=defect, num_train_impacts=2)
    r2 = engine.evaluate(task, defect=defect, num_train_impacts=2)
    assert r1.score == r2.score
    assert r1.priority_class == r2.priority_class


# ─── Explainability ───────────────────────────────────────────────────────────

def test_explanation_present():
    task   = make_task()
    result = engine.evaluate(task)
    assert result.explanation
    assert result.priority_class.value in result.explanation


def test_all_factors_present_in_result():
    task   = make_task()
    defect = make_defect()
    result = engine.evaluate(task, defect=defect, num_train_impacts=1)
    factor_ids = {f.factor_id for f in result.factors}
    expected   = {"criticality", "defect_severity", "safety_critical", "urgency", "train_impact", "task_type", "duration"}
    assert expected == factor_ids


# ─── Provenance ──────────────────────────────────────────────────────────────

def test_engine_version_present():
    task   = make_task()
    result = engine.evaluate(task)
    assert result.engine_version == ENGINE_VERSION


def test_data_state_preserved():
    task   = make_task()
    result = engine.evaluate(task, data_state="MOCKED")
    assert result.data_state == "MOCKED"


# ─── API integration ─────────────────────────────────────────────────────────

def test_api_evaluate_priority(client):
    response = client.post("/api/v1/engine/priority/evaluate", json={"task_id": "TASK-001"})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "score" in data["data"]
    assert "priority_class" in data["data"]
    assert "factors" in data["data"]
    assert len(data["data"]["factors"]) == 7


def test_api_evaluate_priority_not_found(client):
    response = client.post("/api/v1/engine/priority/evaluate", json={"task_id": "NONEXISTENT"})
    assert response.status_code == 404


def test_api_evaluate_batch(client):
    response = client.post("/api/v1/engine/priority/evaluate-batch", json={"task_ids": ["TASK-001"]})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 1


def test_api_batch_with_train_impacts(client):
    response = client.post(
        "/api/v1/engine/priority/evaluate-batch",
        json={"task_ids": ["TASK-001"], "impacts_by_task": {"TASK-001": 3}},
    )
    assert response.status_code == 200
    data = response.json()
    t_factor = next(
        f for f in data["data"][0]["factors"] if f["factor_id"] == "train_impact"
    )
    assert t_factor["raw_value"] == 3


def test_api_task_001_is_critical_priority(client):
    """TASK-001 is CRITICAL criticality, linked to safety-critical defect with 2h urgency — expect HIGH or CRITICAL."""
    response = client.post("/api/v1/engine/priority/evaluate", json={"task_id": "TASK-001", "num_train_impacts": 1})
    data = response.json()
    assert data["data"]["priority_class"] in ["CRITICAL", "HIGH"]