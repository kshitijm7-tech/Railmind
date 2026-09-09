"""Tests — E06 configuration and registry contract (TRD §18, prompt §35)."""

import pytest
from pydantic import ValidationError

from engine._version import (
    DURATION_MODEL_ID,
    DURATION_MODEL_VERSION,
    ENGINE_VERSION,
    FAILURE_RISK_MODEL_ID,
    FAILURE_RISK_MODEL_VERSION,
    PREDICTION_MODEL_ID,
    PREDICTION_MODEL_VERSION,
)
from engine.prediction import (
    ModelStatus,
    PredictionConfig,
    duration_model_metadata,
    failure_risk_model_metadata,
    feature_schema_version,
)


# ---------------------------------------------------------------------------
# Version identity (E01–E05 convention: one entry per engine)
# ---------------------------------------------------------------------------


def test_e06_version_identity_is_declared():
    assert PREDICTION_MODEL_ID == "railmind-predictive-risk"
    assert PREDICTION_MODEL_VERSION == "1.0.0"
    assert DURATION_MODEL_ID == "railmind-duration-prediction"
    assert DURATION_MODEL_VERSION == "1.0.0"
    assert FAILURE_RISK_MODEL_ID == "railmind-failure-risk-prediction"
    assert FAILURE_RISK_MODEL_VERSION == "1.0.0"
    assert ENGINE_VERSION == "0.1.0"  # untouched by E06


# ---------------------------------------------------------------------------
# PredictionConfig defaults and validation
# ---------------------------------------------------------------------------


def test_default_config_has_documented_thresholds():
    cfg = PredictionConfig()
    assert (cfg.risk_threshold_medium, cfg.risk_threshold_high,
            cfg.risk_threshold_critical) == (0.20, 0.45, 0.70)
    assert cfg.default_time_horizon_hours == 720.0
    assert cfg.default_overrun_threshold_minutes == 120.0
    assert cfg.baseline_confidence == 0.5


@pytest.mark.parametrize(
    "medium, high, critical",
    [(0.45, 0.20, 0.70), (0.20, 0.70, 0.45), (0.50, 0.50, 0.90)],
)
def test_non_increasing_thresholds_rejected(medium, high, critical):
    with pytest.raises(ValidationError):
        PredictionConfig(
            risk_threshold_medium=medium,
            risk_threshold_high=high,
            risk_threshold_critical=critical,
        )


def test_out_of_range_thresholds_rejected():
    with pytest.raises(ValidationError):
        PredictionConfig(risk_threshold_medium=1.5)
    with pytest.raises(ValidationError):
        PredictionConfig(risk_threshold_critical=-0.1)


def test_non_positive_saturations_and_horizon_rejected():
    with pytest.raises(ValidationError):
        PredictionConfig(age_saturation_days=0.0)
    with pytest.raises(ValidationError):
        PredictionConfig(service_gap_saturation_days=-1.0)
    with pytest.raises(ValidationError):
        PredictionConfig(default_time_horizon_hours=0.0)
    with pytest.raises(ValidationError):
        PredictionConfig(default_overrun_threshold_minutes=0.0)


# ---------------------------------------------------------------------------
# Risk classification semantics (>= boundary ownership, matching E02)
# ---------------------------------------------------------------------------


def test_classification_boundaries_belong_to_higher_class():
    cfg = PredictionConfig()
    assert cfg.classify_risk(0.0) == "LOW"
    assert cfg.classify_risk(0.199) == "LOW"
    assert cfg.classify_risk(0.20) == "MEDIUM"
    assert cfg.classify_risk(0.449) == "MEDIUM"
    assert cfg.classify_risk(0.45) == "HIGH"
    assert cfg.classify_risk(0.699) == "HIGH"
    assert cfg.classify_risk(0.70) == "CRITICAL"
    assert cfg.classify_risk(1.0) == "CRITICAL"


def test_classification_thresholds_are_e06_owned_not_e02_copied():
    """Prompt §18: E06 risk thresholds must not silently mirror E02's."""
    cfg = PredictionConfig()
    assert (cfg.risk_threshold_medium, cfg.risk_threshold_high,
            cfg.risk_threshold_critical) != (0.40, 0.65, 0.85)


# ---------------------------------------------------------------------------
# Normalization and criticality mapping
# ---------------------------------------------------------------------------


def test_normalize_saturates_at_one_and_clamps_at_zero():
    cfg = PredictionConfig()
    assert cfg.normalize(0.0, 100.0) == 0.0
    assert cfg.normalize(50.0, 100.0) == 0.5
    assert cfg.normalize(150.0, 100.0) == 1.0  # saturation, not extrapolation


def test_criticality_score_uses_shared_e02_mapping():
    cfg = PredictionConfig()
    assert cfg.criticality_score("LOW") == 0.25
    assert cfg.criticality_score("MEDIUM") == 0.50
    assert cfg.criticality_score("HIGH") == 0.75
    assert cfg.criticality_score("CRITICAL") == 1.0


# ---------------------------------------------------------------------------
# TRD §18 registry metadata
# ---------------------------------------------------------------------------


def test_registry_metadata_honest_baseline_status():
    for meta in (duration_model_metadata(), failure_risk_model_metadata()):
        assert meta.algorithm == "deterministic-rules"
        assert meta.status is ModelStatus.DISABLED  # ML artifact does not exist
        assert meta.deterministic_fallback is True
        assert meta.training_dataset_version is None  # no training run to cite
        assert meta.artifact_location is None
        assert meta.identity == f"{meta.model_id}@{meta.version}"
        assert meta.feature_schema_version == feature_schema_version()


def test_feature_schema_version_is_pinned():
    assert feature_schema_version() == "1.0.0"
