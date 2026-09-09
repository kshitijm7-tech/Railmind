"""Tests — E02 factor normalization (deterministic, bounded, explicit maps)."""

import pytest

from engine.priority.configuration import PriorityEngineConfig
from engine.priority.factors import (
    criticality_factor,
    downstream_impact_factor,
    failure_risk_factor,
    overdue_factor,
    safety_factor,
)
from engine.priority.inputs import AssetFailureRisk, PriorityInput


def task(**overrides) -> PriorityInput:
    base = dict(
        task_id="TSK-101",
        section_id="SEC-01",
        criticality="MEDIUM",
        overdue_days=0,
    )
    base.update(overrides)
    return PriorityInput(**base)


# ---------------------------------------------------------------------------
# Criticality (canonical enum → explicit map)
# ---------------------------------------------------------------------------


def test_criticality_enum_mapping_is_explicit():
    cfg = PriorityEngineConfig()
    assert criticality_factor("LOW", cfg).normalized_score == pytest.approx(0.25)
    assert criticality_factor("MEDIUM", cfg).normalized_score == pytest.approx(0.50)
    assert criticality_factor("HIGH", cfg).normalized_score == pytest.approx(0.75)
    assert criticality_factor("CRITICAL", cfg).normalized_score == pytest.approx(1.0)


def test_criticality_monotonic_across_enum_order():
    cfg = PriorityEngineConfig()
    scores = [criticality_factor(c, cfg).normalized_score for c in ("LOW", "MEDIUM", "HIGH", "CRITICAL")]
    assert scores == sorted(scores)


def test_criticality_missing_mapping_is_a_config_error():
    cfg = PriorityEngineConfig()
    broken = cfg.model_copy(update={"criticality_scores": {"LOW": 0.25}})
    with pytest.raises(ValueError, match="criticality_scores config lacks"):
        criticality_factor("CRITICAL", broken)


# ---------------------------------------------------------------------------
# Overdue (linear saturation)
# ---------------------------------------------------------------------------


def test_overdue_minimum_is_zero():
    outcome = overdue_factor(0, PriorityEngineConfig())
    assert outcome.normalized_score == pytest.approx(0.0)


def test_overdue_intermediate_is_linear():
    outcome = overdue_factor(15, PriorityEngineConfig())  # half of 30d saturation
    assert outcome.normalized_score == pytest.approx(0.5)


def test_overdue_saturates_at_bound():
    outcome = overdue_factor(30, PriorityEngineConfig())
    assert outcome.normalized_score == pytest.approx(1.0)


def test_overday_beyond_saturation_is_capped():
    outcome = overdue_factor(45, PriorityEngineConfig())
    assert outcome.normalized_score == pytest.approx(1.0)


def test_overdue_saturation_is_configurable():
    cfg = PriorityEngineConfig(overdue_saturation_days=10)
    assert overdue_factor(5, cfg).normalized_score == pytest.approx(0.5)
    assert overdue_factor(10, cfg).normalized_score == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Failure risk (probability is the bounded score)
# ---------------------------------------------------------------------------


def test_failure_risk_minimum_and_maximum():
    cfg = PriorityEngineConfig()
    low = failure_risk_factor(task(asset_failure_risk=AssetFailureRisk(probability_of_failure=0.0)), cfg)
    high = failure_risk_factor(task(asset_failure_risk=AssetFailureRisk(probability_of_failure=1.0)), cfg)
    assert low.normalized_score == pytest.approx(0.0)
    assert high.normalized_score == pytest.approx(1.0)


def test_failure_risk_intermediate():
    outcome = failure_risk_factor(task(asset_failure_risk=AssetFailureRisk(probability_of_failure=0.42)), PriorityEngineConfig())
    assert outcome.normalized_score == pytest.approx(0.42)


def test_failure_risk_source_records_model_when_present():
    risk = AssetFailureRisk(probability_of_failure=0.7, model_id="risk-xgb", model_version="1.2.0")
    outcome = failure_risk_factor(task(asset_failure_risk=risk), PriorityEngineConfig())
    assert outcome.source == "risk-model:risk-xgb@1.2.0"


def test_failure_risk_absent_is_explicitly_not_present():
    outcome = failure_risk_factor(task(), PriorityEngineConfig())
    assert outcome.present is False
    assert "asset_failure_risk" in outcome.missing_reason


# ---------------------------------------------------------------------------
# Safety (flag dominates, task-type prior otherwise)
# ---------------------------------------------------------------------------


def test_safety_explicit_flag_scores_full():
    outcome = safety_factor(task(is_safety_relevant=True), PriorityEngineConfig())
    assert outcome.normalized_score == pytest.approx(1.0)


def test_safety_explicit_false_overrides_task_type_prior():
    # An EMERGENCY task explicitly flagged not-safety-relevant → 0.0
    outcome = safety_factor(task(task_type="EMERGENCY", is_safety_relevant=False), PriorityEngineConfig())
    assert outcome.normalized_score == pytest.approx(0.0)


def test_safety_task_type_priors_are_monotonic():
    cfg = PriorityEngineConfig()
    scores = [
        safety_factor(task(task_type=t), cfg).normalized_score
        for t in ("PREVENTIVE", "INSPECTION", "CORRECTIVE", "EMERGENCY")
    ]
    assert scores == sorted(scores)


def test_safety_task_type_prior_is_scaled_by_configured_share():
    cfg = PriorityEngineConfig()
    prior = cfg.safety_task_type_scores["CORRECTIVE"]
    outcome = safety_factor(task(task_type="CORRECTIVE"), cfg)
    assert outcome.normalized_score == pytest.approx(prior * cfg.safety_task_type_weight_share)


def test_safety_absent_is_explicitly_not_present():
    outcome = safety_factor(task(), PriorityEngineConfig())
    assert outcome.present is False


# ---------------------------------------------------------------------------
# Downstream impact (trains/day saturation)
# ---------------------------------------------------------------------------


def test_downstream_impact_boundaries():
    cfg = PriorityEngineConfig()
    assert downstream_impact_factor(task(trains_per_day=0), cfg).normalized_score == pytest.approx(0.0)
    assert downstream_impact_factor(task(trains_per_day=30), cfg).normalized_score == pytest.approx(0.5)
    assert downstream_impact_factor(task(trains_per_day=60), cfg).normalized_score == pytest.approx(1.0)
    assert downstream_impact_factor(task(trains_per_day=120), cfg).normalized_score == pytest.approx(1.0)


def test_downstream_impact_absent_is_explicitly_not_present():
    outcome = downstream_impact_factor(task(), PriorityEngineConfig())
    assert outcome.present is False
