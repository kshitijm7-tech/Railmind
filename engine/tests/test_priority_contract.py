"""Tests — E02 contract compatibility (AC-001, §19).

The engine must be able to consume the canonical task representations used by
the other agents: the frontend's canonical fixture tasks (the §12 dataset
vocabulary: TSK-101, overdue_days, criticality) and the backend's Pydantic
``MaintenanceTask`` shape. These tests exercise the intended adapter mapping
without importing frontend or backend code.
"""

from datetime import datetime, timezone

import pytest

from engine.priority.engine import PriorityEngine
from engine.priority.inputs import PriorityInput


def from_frontend_fixture(task: dict) -> PriorityInput:
    """Adapter for ``frontend/fixtures/demoCorridor.ts`` task records.

    Mirrors the canonical §12 dataset vocabulary (task_id, criticality,
    overdue_days, duration_estimates) plus the safety flag the fixture
    exposes via ``task_type``.
    """
    return PriorityInput(
        task_id=task["task_id"],
        section_id=task["section_id"],
        asset_id=task.get("asset_id"),
        criticality=task["criticality"],
        overdue_days=task.get("overdue_days", 0),
        task_type=task.get("task_type"),
        is_safety_relevant=task.get("is_safety_relevant"),
        trains_per_day=task.get("trains_per_day"),
    )


def from_backend_model(task) -> PriorityInput:
    """Adapter for ``backend/app/domain/models/maintenance.py::MaintenanceTask``.

    The backend model has no overdue counter or traffic volume — those are
    recorded contract gaps (docs/E02_Report.md); the adapter maps what exists.
    """
    return PriorityInput(
        task_id=task.task_id,
        section_id=task.section_id,
        asset_id=task.asset_id,
        criticality=task.criticality.value,
        overdue_days=0,
        requires_power_block=task.requires_power_block,
        requires_traffic_block=task.requires_traffic_block,
    )


def test_frontend_fixture_task_is_consumable():
    # Vocabulary of frontend/fixtures/demoCorridor.ts::TSK-101
    fixture_task = {
        "task_id": "TSK-101",
        "section_id": "SEC-04",
        "asset_id": "AST-TRK-01",
        "criticality": "CRITICAL",
        "overdue_days": 3,
        "task_type": "Defect",  # fixture uses blueprint §11.2 task types
        "duration_estimates": {"expected_min": 180, "p10_min": 150, "p90_min": 240},
    }
    engine = PriorityEngine()
    result = engine.evaluate(from_frontend_fixture(fixture_task))
    assert result.task_id == "TSK-101"
    assert result.score > 0.0
    assert result.priority_class in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


def test_frontend_fixture_defect_type_uses_safety_prior():
    # Blueprint §11.2 vocabulary "Defect" is accepted (case-insensitive) and
    # receives a corrective-like safety prior (0.75 × share 0.5 = 0.375).
    fixture_task = {
        "task_id": "TSK-102",
        "section_id": "SEC-04",
        "criticality": "CRITICAL",
        "overdue_days": 3,
        "task_type": "Defect",
    }
    engine = PriorityEngine()
    result = engine.evaluate(from_frontend_fixture(fixture_task))
    safety = next(f for f in result.factor_scores if f.factor == "safety")
    assert safety.normalized_score == pytest.approx(0.375)
    assert safety.source == "config:safety_task_type_scores"


def test_backend_pydantic_task_is_consumable():
    # Minimal object exposing the backend MaintenanceTask attribute surface.
    class _BackendTask:
        task_id = "TASK-001"
        section_id = "SEC-001"
        asset_id = "AST-101"
        requires_power_block = True
        requires_traffic_block = False

        class _Crit:
            value = "HIGH"

        criticality = _Crit()

    engine = PriorityEngine()
    result = engine.evaluate(from_backend_model(_BackendTask()))
    assert result.task_id == "TASK-001"
    assert result.metadata["asset_id"] == "AST-101"
    # Only criticality is known; safety and risk are absent → excluded and
    # weights renormalised: score = 0.75 × 0.30/(0.30+0.20+0.10) = 0.45.
    assert result.score == pytest.approx(0.45)
    assert result.weight_total == pytest.approx(1.0)


def test_priorities_are_comparable_across_tasks():
    engine = PriorityEngine()
    critical_overdue = engine.evaluate(
        from_frontend_fixture(
            {"task_id": "TSK-A", "section_id": "SEC-04", "criticality": "CRITICAL", "overdue_days": 30}
        )
    )
    routine = engine.evaluate(
        from_frontend_fixture(
            {"task_id": "TSK-B", "section_id": "SEC-01", "criticality": "LOW", "overdue_days": 0}
        )
    )
    assert critical_overdue.score > routine.score
    assert critical_overdue.priority_class == "CRITICAL"
    assert routine.priority_class == "LOW"
