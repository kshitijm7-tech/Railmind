"""E06 contract tests — architecture boundaries (prompt §24).

AST/import-level pins protecting the deterministic pipeline:
- E01–E05 never import E06 (dependency direction E06 → upstream only);
- E06 contains no randomness, no clock reads, no network/persistence imports;
- E06 does not reimplement E02 priority or E05 Monte Carlo (token scan on
  the *predictor* modules only, where duplication would matter);
- the public export surface is exactly the documented set.
"""

import ast
import inspect

import pytest

import engine
from engine._version import (
    DURATION_MODEL_ID,
    FAILURE_RISK_MODEL_ID,
    PREDICTION_MODEL_ID,
)
from engine.prediction.duration import duration_model_metadata
from engine.prediction.failure_risk import failure_risk_model_metadata


# ---------------------------------------------------------------------------
# Dependency direction: nothing downstream of E06 may import it
# ---------------------------------------------------------------------------


def test_deterministic_engines_never_import_e06():
    import engine.optimization.evaluation
    import engine.priority.engine
    import engine.scenario.comparison
    import engine.scenario.result
    import engine.simulation.simulator

    for module in (
        engine.optimization.evaluation,
        engine.priority.engine,
        engine.scenario.comparison,
        engine.scenario.result,
        engine.simulation.simulator,
    ):
        source = inspect.getsource(module)
        assert "engine.prediction" not in source, (
            f"{module.__name__} illegally depends on E06"
        )


# ---------------------------------------------------------------------------
# Determinism containment: no RNG, no clocks inside E06
# ---------------------------------------------------------------------------


def _source_modules():
    import engine.prediction.configuration as configuration
    import engine.prediction.duration as duration
    import engine.prediction.failure_risk as failure_risk
    import engine.prediction.inputs as inputs
    import engine.prediction.interface as interface
    import engine.prediction.registry as registry
    import engine.prediction.result as result

    return (configuration, duration, failure_risk, inputs, interface, registry, result)


def test_e06_contains_no_randomness():
    for module in _source_modules():
        tree = ast.parse(inspect.getsource(module))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [a.name for a in node.names]
                assert not any("random" in n for n in names), (
                    f"{module.__name__} imports randomness at line {node.lineno}"
                )
            elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                assert node.value.id != "random", (
                    f"{module.__name__} uses random.{node.attr}"
                )


def test_e06_contains_no_clock_reads():
    forbidden_calls = {"now", "utcnow", "time", "perf_counter", "monotonic"}
    for module in _source_modules():
        tree = ast.parse(inspect.getsource(module))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                assert node.func.attr not in forbidden_calls, (
                    f"{module.__name__} reads a clock: "
                    f"{node.func.attr}() at line {node.lineno}"
                )


def test_e06_imports_no_network_or_persistence_libraries():
    forbidden = {"fastapi", "sqlalchemy", "httpx", "requests", "socket",
                 "urllib", "redis", "pymongo"}
    for module in _source_modules():
        tree = ast.parse(inspect.getsource(module))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    assert root not in forbidden, (
                        f"{module.__name__} imports {alias.name}"
                    )
            elif isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".")[0]
                assert root not in forbidden, (
                    f"{module.__name__} imports from {node.module}"
                )


def test_e06_does_not_import_ml_libraries():
    """No ML dependency exists in the repo — E06 must not grow one silently."""
    forbidden = {"xgboost", "sklearn", "scipy", "numpy", "pandas", "torch"}
    for module in _source_modules():
        tree = ast.parse(inspect.getsource(module))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    assert root not in forbidden, (
                        f"{module.__name__} imports ML library {alias.name}"
                    )
            elif isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".")[0]
                assert root not in forbidden, (
                    f"{module.__name__} imports from {node.module}"
                )


# ---------------------------------------------------------------------------
# No duplication of E02 priority / E05 simulation logic (predictor bodies)
# ---------------------------------------------------------------------------


def test_predictors_do_not_reimplement_priority_or_simulation():
    import engine.prediction.duration as duration
    import engine.prediction.failure_risk as failure_risk

    for module in (duration, failure_risk):
        source = inspect.getsource(module)
        for token in (
            "criticality_weight", "overdue_weight", "downstream_impact_weight",
            "normalized_weights",  # E02 weighted-priority machinery
            "monte_carlo", "P10, P90] band", "draws", "Random(",  # E05 sampling
            "unscheduled_priority_weight", "objective_weights",  # E03 objective
        ):
            assert token not in source, (
                f"{module.__name__} duplicates upstream engine logic: {token!r}"
            )


# ---------------------------------------------------------------------------
# TRD §17 protocol conformance
# ---------------------------------------------------------------------------


def test_predictors_implement_full_trd_17_protocol():
    from engine.prediction import DurationPredictor, FailureRiskPredictor

    for predictor in (DurationPredictor(), FailureRiskPredictor()):
        for method in ("predict", "predict_with_uncertainty", "get_version", "explain"):
            assert callable(getattr(predictor, method, None)), (
                f"{type(predictor).__name__} misses TRD §17 method {method!r}"
            )


def test_protocol_is_runtime_checkable_and_satisfied():
    from engine.prediction import DurationPredictor, FailureRiskPredictor
    from engine.prediction.interface import PredictionModel

    assert isinstance(DurationPredictor(), PredictionModel)
    assert isinstance(FailureRiskPredictor(), PredictionModel)


# ---------------------------------------------------------------------------
# Registry + provenance identity (TRD §18, prompt §15)
# ---------------------------------------------------------------------------


def test_registry_records_carry_honest_ids():
    d = duration_model_metadata()
    f = failure_risk_model_metadata()
    assert d.model_id == DURATION_MODEL_ID == "railmind-duration-prediction"
    assert f.model_id == FAILURE_RISK_MODEL_ID == "railmind-failure-risk-prediction"
    assert d.model_id != f.model_id  # distinct models, one umbrella identity
    assert PREDICTION_MODEL_ID == "railmind-predictive-risk"


def test_results_stamp_their_own_model_identity():
    from engine.prediction import DurationPredictor, FailureRiskPredictor
    from engine.prediction.inputs import (
        DurationFeatures, FailureRiskFeatures,
    )

    d = DurationPredictor().predict(
        DurationFeatures(
            task_id="T", task_type="INSPECTION", department="ENG",
            asset_type="TRACK", section_criticality="LOW", crew_size=1,
            historical_duration_minutes=30.0, time_of_day_minutes=600.0,
            days_since_last_similar_task=1.0,
        )
    )
    f = FailureRiskPredictor().predict(
        FailureRiskFeatures(
            asset_id="A", asset_age_days=100.0, asset_type="TRACK",
            maintenance_history=1, failure_history=0, criticality="LOW",
            days_since_last_service=10.0, task_backlog=0, condition_score=95.0,
        )
    )
    assert (d.model_id, d.model_version) == (DURATION_MODEL_ID, d.model_version)
    assert (f.model_id, f.model_version) == (FAILURE_RISK_MODEL_ID, f.model_version)
    assert d.engine_version == engine.ENGINE_VERSION


# ---------------------------------------------------------------------------
# Export surface (E01–E05 convention: intentional public names only)
# ---------------------------------------------------------------------------


def test_engine_exports_expose_e06_public_surface():
    expected = {
        "PredictionModel", "ModelPredictionError", "ModelNotAvailableError",
        "ModelMetadata", "ModelStatus", "feature_schema_version",
        "DurationFeatures", "DurationPredictionWindow", "FailureRiskFeatures",
        "validate_duration_features", "validate_failure_risk_features",
        "DurationPredictor", "duration_model_metadata", "P10_FACTOR",
        "P90_FACTOR", "FailureRiskPredictor", "failure_risk_model_metadata",
        "WEIGHTS", "ASSET_TYPE_SCORES", "DurationPredictionResult",
        "FailureRiskPredictionResult", "PredictionBase", "PredictionProvenance",
        "PredictionConfig", "CRITICALITY_SCORES",
    }
    missing = expected - set(engine.__all__)
    assert not missing, f"E06 exports missing from engine.__all__: {missing}"
    for name in (
        "PREDICTION_MODEL_ID", "PREDICTION_MODEL_VERSION",
        "DURATION_MODEL_ID", "DURATION_MODEL_VERSION",
        "FAILURE_RISK_MODEL_ID", "FAILURE_RISK_MODEL_VERSION",
    ):
        assert name in engine.__all__


def test_private_helpers_stay_internal():
    for name in ("require_probability", "require_finite", "model_identity",
                 "_resolve_threshold", "_require_criticality"):
        assert name not in engine.__all__


# ---------------------------------------------------------------------------
# Inference determinism through the public API
# ---------------------------------------------------------------------------


def test_repeated_inference_is_byte_identical():
    from engine.prediction import (
        DurationFeatures, DurationPredictor, FailureRiskFeatures,
        FailureRiskPredictor,
    )

    f = DurationFeatures(
        task_id="T-D", task_type="PREVENTIVE", department="P-WAY",
        asset_type="TRACK", section_criticality="HIGH", crew_size=3,
        historical_duration_minutes=120.0, time_of_day_minutes=1380.0,
        days_since_last_similar_task=200.0,
    )
    a = DurationPredictor().predict(f).model_dump()
    b = DurationPredictor().predict(f).model_dump()
    assert a == b

    g = FailureRiskFeatures(
        asset_id="A-D", asset_age_days=5000.0, asset_type="SIGNAL",
        maintenance_history=2, failure_history=1, criticality="MEDIUM",
        days_since_last_service=30.0, task_backlog=1, condition_score=80.0,
    )
    c = FailureRiskPredictor().predict(g).model_dump()
    d = FailureRiskPredictor().predict(g).model_dump()
    assert c == d
