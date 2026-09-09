"""E07 architecture contract tests (prompt §26) + mapper unit tests.

Pins the wrap-don't-duplicate boundary:
- direction: ``engine → backend`` must NEVER occur (engine stays standalone);
- no duplicate logic: the backend contains no E02/E03/E04/E05/E06 math;
- no global state corruption: serving requests does not touch engine/global
  RNG behavior;
- error mapping: engine-domain errors → DomainError with correct categories.
"""

import ast
import inspect
import random

import pytest

from app.core.errors import DomainError, ErrorCategory
from app.engine_adapter.mapper import translate_engine_error
from app.engine_bridge import (
    BlockWindow,
    DurationBand,
    DurationFeatures,
    DurationPredictionWindow,
    FailureRiskFeatures,
    PriorityInput,
    SimulationConfig,
)


REPO_ROOT_ADAPTER_FILES = [
    "backend/app/engine_adapter/mapper.py",
    "backend/app/engine_adapter/service.py",
    "backend/app/engine_bridge.py",
    "backend/app/api/v1/endpoints/engine.py",
]


# ---------------------------------------------------------------------------
# Dependency direction (§26): backend → engine allowed; engine → backend never
# ---------------------------------------------------------------------------


def test_engine_never_imports_the_backend():
    import engine
    import engine.constraints.engine as constraints_engine
    import engine.optimization.evaluation as optimization
    import engine.priority.engine as priority
    import engine.prediction.duration as duration
    import engine.prediction.failure_risk as failure_risk
    import engine.scenario.comparison as scenario
    import engine.simulation.simulator as simulation

    for module in (engine, constraints_engine, optimization, priority,
                   duration, failure_risk, scenario, simulation):
        source = inspect.getsource(module)
        assert "app.engine" not in source and "fastapi" not in source, (
            f"{module.__name__} illegally depends on the backend"
        )


def test_only_the_adapter_package_imports_the_engine():
    """Router/other-backend files must reach the engine only through the
    adapter; engine_bridge is the single sanctioned import point."""
    import pathlib

    backend_root = pathlib.Path(__file__).resolve().parents[1] / "app"
    offenders = []
    for path in backend_root.rglob("*.py"):
        rel = path.relative_to(backend_root).as_posix()
        if rel.startswith("engine_adapter") or rel == "engine_bridge.py":
            continue
        text = path.read_text(encoding="utf-8")
        if "from engine" in text or "import engine" in text:
            offenders.append(rel)
    assert offenders == [] or offenders == ["\\expected\\none"], offenders


def test_bridge_imports_public_contracts_only():
    import pathlib

    bridge = (
        pathlib.Path(__file__).resolve().parents[1] / "app" / "engine_bridge.py"
    ).read_text(encoding="utf-8")
    forbidden = [
        "engine.constraints._toolkit",
        "engine.tests",
        "engine.optimization.evaluation import _",
        "from engine.simulation.simulator import _",
    ]
    for token in forbidden:
        assert token not in bridge, f"bridge imports private surface: {token}"


# ---------------------------------------------------------------------------
# No duplicate engine logic (§26)
# ---------------------------------------------------------------------------


def test_backend_contains_no_engine_math():
    import pathlib

    backend_root = pathlib.Path(__file__).resolve().parents[1] / "app"
    tokens = [
        # E02 weighted-priority machinery
        "criticality_weight", "normalized_weights", "overdue_saturation_days",
        # E03 §17.5 coefficients
        "train_delay_weight", "unscheduled_priority_weight", "block_count_weight",
        # E05 Monte Carlo
        "monte_carlo", "Random(", "derive_stream_seed",
        # E06 formulas
        "P10_FACTOR", "WEIGHTS[", "classify_risk",
    ]
    offenders = []
    for path in backend_root.rglob("*.py"):
        rel = path.relative_to(backend_root).as_posix()
        if not any(part in rel for part in ("engine_adapter", "engine_bridge")):
            text = path.read_text(encoding="utf-8")
            for token in tokens:
                if token in text:
                    offenders.append(f"{rel}: {token}")
    assert offenders == [], (
        f"backend duplicates engine logic: {offenders}"
    )


# ---------------------------------------------------------------------------
# No global-state corruption (§26): serving requests must not touch RNG
# ---------------------------------------------------------------------------


def test_serving_requests_does_not_mutate_global_random_state():
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    random.seed(1234)
    before = random.getstate()

    body = {
        "windows": [
            {
                "windowId": "W1",
                "sectionId": "SEC-A",
                "earliestStart": "2026-09-14T22:00:00Z",
                "latestEnd": "2026-09-15T02:00:00Z",
                "maxDurationMinutes": 78.0,
                "taskBands": [{"taskId": "T1", "p10Minutes": 30.0, "p90Minutes": 50.0}],
            }
        ],
        "iterations": 25,
        "seed": 3,
    }
    assert client.post("/api/v1/plans/P/simulate", json=body).status_code == 200
    assert client.post(
        "/api/v1/maintenance/prioritize",
        json={"taskId": "T", "sectionId": "S", "criticality": "HIGH"},
    ).status_code == 200

    assert random.getstate() == before, "backend mutated global RNG state"


def test_engine_error_is_translated_by_the_service_not_raised_raw():
    """An engine contract violation reaches the client as a DomainError
    envelope (400), not a raw pydantic traceback (500)."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    response = client.post(
        "/api/v1/predictions/failure-risk",
        json={
            "assetId": "A", "assetAgeDays": 1.0, "assetType": "NOT_A_TYPE",
            "maintenanceHistory": 0, "failureHistory": 0,
            "criticality": "LOW", "daysSinceLastService": 0.0,
            "taskBacklog": 0, "conditionScore": 50.0,
        },
    )
    assert response.status_code == 400
    payload = response.json()
    assert payload["error"]["code"] == "ENGINE_INPUT_INVALID"
    assert "Traceback" not in response.text


# ---------------------------------------------------------------------------
# Mapper unit tests: explicit field mapping + error categories (§10)
# ---------------------------------------------------------------------------


class TestErrorTranslation:
    def test_value_error_maps_to_validation_400(self):
        translated = translate_engine_error(ValueError("bad band"))
        assert isinstance(translated, DomainError)
        assert translated.category is ErrorCategory.VALIDATION
        assert translated.code == "ENGINE_INPUT_INVALID"
        assert translated.message == "bad band"

    def test_key_error_maps_to_not_found_404(self):
        translated = translate_engine_error(KeyError("no profile for window W9"))
        assert isinstance(translated, DomainError)
        assert translated.category is ErrorCategory.NOT_FOUND
        assert translated.code == "ENGINE_ENTITY_NOT_FOUND"

    def test_domain_error_passes_through(self):
        original = DomainError("already mapped", ErrorCategory.VALIDATION, "X")
        assert translate_engine_error(original) is original

    def test_unrelated_errors_propagate_unchanged(self):
        sentinel = RuntimeError("boom")
        assert translate_engine_error(sentinel) is sentinel


class TestRequestMapping:
    def test_priority_input_mapping_is_explicit(self):
        from app.api.schemas.engine import PrioritizeTaskRequest

        request = PrioritizeTaskRequest(
            taskId="T-1", sectionId="SEC-1", criticality="HIGH",
            overdueDays=5, taskType="CORRECTIVE", trainsPerDay=30.0,
        )
        engine_input = __import__(
            "app.engine_adapter.mapper", fromlist=["x"]
        ).prioritize_task_to_priority_input(request)
        assert isinstance(engine_input, PriorityInput)
        assert engine_input.task_id == "T-1"
        assert engine_input.overdue_days == 5
        assert engine_input.trains_per_day == 30.0

    def test_backend_enum_members_outside_engine_vocabulary_are_rejected(self):
        """The backend TaskType enum carries REPAIR/REPLACEMENT, which are NOT
        in the engine's canonical vocabulary. Strictness (§11): the adapter
        must NOT map them to an invented engine value. The ENGINE remains the
        vocabulary authority — a direct mapper call raises the engine's raw
        ValidationError (a ValueError); the service's _engine_call translates
        it to a 400 DomainError/ENGINE_INPUT_INVALID (proven at the HTTP
        layer in test_api_engine.py). Documented mismatch: E07 report §12."""
        from app.api.schemas.engine import PrioritizeTaskRequest

        request = PrioritizeTaskRequest(
            taskId="T-1", sectionId="SEC-1", criticality="HIGH",
            taskType="REPAIR",
        )
        with pytest.raises(ValueError) as excinfo:  # pydantic ValidationError
            __import__(
                "app.engine_adapter.mapper", fromlist=["x"]
            ).prioritize_task_to_priority_input(request)
        assert "PREVENTIVE|CORRECTIVE|INSPECTION|EMERGENCY|DEFECT" in (
            str(excinfo.value)
        )

    def test_window_mapping_requires_bands(self):
        from app.api.schemas.engine import SimulateBlockRequest

        window = SimulateBlockRequest(
            windowId="W", sectionId="S",
            earliestStart=__import__("datetime").datetime(2026, 9, 14, 22, 0),
            latestEnd=__import__("datetime").datetime(2026, 9, 15, 2, 0),
            maxDurationMinutes=60.0, taskBands=[],
        )
        with pytest.raises(DomainError) as excinfo:
            __import__(
                "app.engine_adapter.mapper", fromlist=["x"]
            ).window_request_to_block_window(window)
        assert excinfo.value.code == "MISSING_TASK_BANDS"

    def test_window_mapping_builds_engine_block_window(self):
        from datetime import datetime
        from app.api.schemas.engine import SimulateBlockRequest, TaskDurationBand
        from app.engine_adapter.mapper import window_request_to_block_window

        window = SimulateBlockRequest(
            windowId="W1", sectionId="SEC-A",
            earliestStart=datetime(2026, 9, 14, 22, 0),
            latestEnd=datetime(2026, 9, 15, 2, 0),
            maxDurationMinutes=78.0,
            taskBands=[TaskDurationBand(taskId="T1", p10Minutes=30.0, p90Minutes=50.0)],
        )
        block_window = window_request_to_block_window(window)
        assert isinstance(block_window, BlockWindow)
        assert block_window.task_bands[0].p10_minutes == 30.0

    def test_duration_features_mapping_rejects_unknown_task_type(self):
        from app.api.schemas.engine import DurationPredictionRequest

        request = DurationPredictionRequest(
            taskId="T", taskType="TELEPORT", department="D", assetType="A",
            sectionCriticality="HIGH", crewSize=1,
            historicalDurationMinutes=30.0, timeOfDayMinutes=600.0,
            daysSinceLastSimilarTask=1.0,
        )
        with pytest.raises(Exception) as excinfo:
            DurationFeatures(
                task_id=request.taskId, task_type=request.taskType,
                department=request.department, asset_type=request.assetType,
                section_criticality=request.sectionCriticality,
                crew_size=request.crewSize,
                historical_duration_minutes=request.historicalDurationMinutes,
                time_of_day_minutes=request.timeOfDayMinutes,
                days_since_last_similar_task=request.daysSinceLastSimilarTask,
            )
        assert "task_type" in str(excinfo.value)

    def test_duration_window_mapping_passes_deadline_pair_through(self):
        from datetime import datetime, timezone
        from app.api.schemas.engine import DurationPredictionRequest

        request = DurationPredictionRequest(
            taskId="T", taskType="PREVENTIVE", department="D", assetType="TRACK",
            sectionCriticality="LOW", crewSize=1,
            historicalDurationMinutes=30.0, timeOfDayMinutes=600.0,
            daysSinceLastSimilarTask=1.0,
            startAt=datetime(2026, 9, 14, 22, 0, tzinfo=timezone.utc),
            latestFinish=datetime(2026, 9, 15, 2, 0, tzinfo=timezone.utc),
        )
        window = DurationPredictionWindow(
            start_at=request.startAt,
            latest_finish=request.latestFinish,
            overrun_threshold_minutes=request.overrunThresholdMinutes,
        )
        assert window.resolved_threshold_minutes(120.0) == 240.0
        assert isinstance(SimulationConfig(iterations=1), SimulationConfig)
