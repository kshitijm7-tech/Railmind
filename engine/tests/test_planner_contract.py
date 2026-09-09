"""E09 architecture/contract tests — dependency direction, RNG discipline,
ML-truthfulness, ortools containment (mirrors the E05/E06 scan patterns,
AST-based rather than substring matching where possible).
"""

import ast
import pathlib

import pytest

ENGINE_ROOT = pathlib.Path(__file__).resolve().parents[1]
DELAY_ROOT = ENGINE_ROOT / "delay"
PLANNER_ROOT = ENGINE_ROOT / "planner"


def _py_files(root: pathlib.Path):
    return sorted(root.rglob("*.py"))


def _imports_of(path: pathlib.Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module.split(".")[0])
    return modules


class TestDependencyContainment:
    """§21/§22: ortools only inside engine.planner; delay stays stdlib."""

    def test_ortools_confined_to_planner_package(self):
        offenders = [
            str(p.relative_to(ENGINE_ROOT))
            for p in _py_files(ENGINE_ROOT)
            if "ortools" in _imports_of(p)
            and "planner" not in p.relative_to(ENGINE_ROOT).parts
        ]
        assert offenders == [], offenders

    def test_delay_package_never_imports_ortools_or_networkx(self):
        for path in _py_files(DELAY_ROOT):
            modules = _imports_of(path)
            assert "ortools" not in modules, path
            assert "networkx" not in modules, path

    def test_planner_never_imports_backend(self):
        for path in _py_files(PLANNER_ROOT):
            modules = _imports_of(path)
            for forbidden in ("fastapi", "app", "backend"):
                assert forbidden not in modules, (path, forbidden)

    def test_engine_never_imports_backend(self):
        offenders = [
            str(p.relative_to(ENGINE_ROOT))
            for p in _py_files(ENGINE_ROOT)
            if _imports_of(p) & {"fastapi", "app", "backend", "sqlalchemy"}
        ]
        assert offenders == [], offenders


class TestRandomnessDiscipline:
    """E09 is deterministic: no global RNG, no clock reads in modules."""

    def test_no_global_random_module_usage(self):
        for root in (DELAY_ROOT, PLANNER_ROOT):
            for path in _py_files(root):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        assert not any(
                            alias.name == "random" for alias in node.names
                        ), path
                    if isinstance(node, ast.ImportFrom):
                        assert (node.module or "") != "random", path

    def test_no_datetime_now_in_engine_modules(self):
        """E09 reads no wall clock inside solver semantics (the only
        perf_counter use is the solve-evidence timing, which is explicit)."""
        for path in _py_files(PLANNER_ROOT):
            text = path.read_text(encoding="utf-8")
            assert "datetime.now(" not in text, path
            assert "utcnow(" not in text, path

    def test_no_network_or_persistence_imports(self):
        forbidden = {"socket", "urllib", "http", "requests", "sqlite3", "pickle"}
        for root in (DELAY_ROOT, PLANNER_ROOT):
            for path in _py_files(root):
                modules = _imports_of(path)
                assert not (modules & forbidden), (path, modules & forbidden)


class TestPublicExports:
    def test_engine_exports_e09_identity(self):
        import engine

        for name in (
            "DELAY_MODEL_ID",
            "DELAY_MODEL_VERSION",
            "PLANNER_MODEL_ID",
            "PLANNER_MODEL_VERSION",
            "CpSatPlanner",
            "PlannerInput",
            "PlannerResult",
            "GraphPropagationDelayModel",
            "DelayFeatures",
            "DelayPredictionResult",
        ):
            assert name in engine.__all__, name
            assert hasattr(engine, name), name

    def test_version_ids_are_distinct(self):
        from engine import (
            DELAY_MODEL_ID,
            PLANNER_MODEL_ID,
            PRIORITY_MODEL_ID,
            SIMULATION_MODEL_ID,
        )

        ids = {DELAY_MODEL_ID, PLANNER_MODEL_ID, PRIORITY_MODEL_ID, SIMULATION_MODEL_ID}
        assert len(ids) == 4

    def test_result_contracts_round_trip(self):
        from datetime import datetime, timezone

        from engine import (
            AffectedTrain,
            DelayFeatures,
            GraphPropagationDelayModel,
            PlannerInput,
            TaskInput,
            WindowInput,
        )
        from engine.priority.result import PriorityResult

        t0 = datetime(2026, 9, 14, 22, 0, tzinfo=timezone.utc)
        delay = GraphPropagationDelayModel().predict(
            DelayFeatures(
                window_id="W1", section_id="S", earliest_start=t0,
                latest_end=t0.replace(hour=23), time_of_day_minutes=0.0,
                historical_delay_minutes=5.0,
                affected_trains=[
                    AffectedTrain(train_id="R", priority=1.0, route=["S"])
                ],
            )
        )
        data = PlannerInput(
            tasks=[
                TaskInput(task_id="T", duration_minutes=30, department="S&T",
                          priority=PriorityResult(task_id="T", score=0.5, priority_class="HIGH"))
            ],
            windows=[
                WindowInput(window_id="W1", section_id="S", earliest_start=t0,
                            latest_end=t0.replace(hour=23),
                            max_duration_minutes=60.0,
                            qualified_departments=["S&T"])
            ],
            delay_results={"W1": delay},
        )
        restored = PlannerInput.model_validate_json(data.model_dump_json())
        assert restored == data
