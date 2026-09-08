"""Tests — E02 configuration boundary: weights, thresholds, policies."""

import pytest
from pydantic import ValidationError

from engine.priority.configuration import PriorityEngineConfig
from engine.priority.missing_data import MissingDataPolicy


def test_default_weights_match_prd_fr_mi_001():
    cfg = PriorityEngineConfig()
    assert cfg.criticality_weight == pytest.approx(0.30)
    assert cfg.overdue_weight == pytest.approx(0.20)
    assert cfg.failure_risk_weight == pytest.approx(0.20)
    assert cfg.safety_weight == pytest.approx(0.20)
    assert cfg.downstream_impact_weight == pytest.approx(0.10)
    assert cfg.weights_sum() == pytest.approx(1.0)


def test_default_missing_data_policy_is_exclude():
    assert PriorityEngineConfig().missing_data_policy is MissingDataPolicy.EXCLUDE_FACTOR


def test_negative_weight_rejected():
    with pytest.raises(ValidationError):
        PriorityEngineConfig(criticality_weight=-0.1)


def test_all_zero_weights_rejected_by_normalized_weights():
    cfg = PriorityEngineConfig(
        criticality_weight=0.0,
        overdue_weight=0.0,
        failure_risk_weight=0.0,
        safety_weight=0.0,
        downstream_impact_weight=0.0,
    )
    with pytest.raises(ValueError, match="all priority weights are zero"):
        cfg.normalized_weights()


def test_engine_constructor_rejects_all_zero_weights():
    from engine.priority.engine import PriorityEngine

    with pytest.raises(ValueError, match="all priority weights are zero"):
        PriorityEngine(
            PriorityEngineConfig(
                criticality_weight=0.0,
                overdue_weight=0.0,
                failure_risk_weight=0.0,
                safety_weight=0.0,
                downstream_impact_weight=0.0,
            )
        )


def test_weights_not_summing_to_one_are_renormalised():
    cfg = PriorityEngineConfig(
        criticality_weight=0.6,
        overdue_weight=0.4,
        failure_risk_weight=0.4,
        safety_weight=0.4,
        downstream_impact_weight=0.2,
    )  # sums to 2.0
    weights = cfg.normalized_weights()
    assert sum(weights.values()) == pytest.approx(1.0)
    assert weights["criticality"] == pytest.approx(0.30)  # 0.6 / 2.0


def test_thresholds_must_be_strictly_increasing():
    with pytest.raises(ValidationError):
        PriorityEngineConfig(threshold_medium=0.65, threshold_high=0.65)
    with pytest.raises(ValidationError):
        PriorityEngineConfig(threshold_high=0.90, threshold_critical=0.85)


def test_zero_total_weight_configuration_is_explicit_not_silent():
    # A configuration with weights summing to zero must fail loudly, never
    # produce a misleading priority score.
    cfg = PriorityEngineConfig(
        criticality_weight=0.0,
        overdue_weight=0.0,
        failure_risk_weight=0.0,
        safety_weight=0.0,
        downstream_impact_weight=0.5,
    )
    # This one is valid (0.5 total); zero the last one to trigger failure.
    zeroed = cfg.model_copy(update={"downstream_impact_weight": 0.0})
    with pytest.raises(ValueError):
        zeroed.normalized_weights()


def test_saturation_bounds_must_be_positive():
    with pytest.raises(ValidationError):
        PriorityEngineConfig(overdue_saturation_days=0)
    with pytest.raises(ValidationError):
        PriorityEngineConfig(downstream_trains_per_day_saturation=-5)
