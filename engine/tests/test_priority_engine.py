"""Tests — E02 engine: score math, classification, policies, determinism, explainability."""

import math

import pytest

from engine._version import ENGINE_VERSION, PRIORITY_MODEL_ID, PRIORITY_MODEL_VERSION
from engine.priority.configuration import PriorityEngineConfig
from engine.priority.engine import PriorityEngine, classify
from engine.priority.inputs import AssetFailureRisk, PriorityInput
from engine.priority.missing_data import MissingDataPolicy
from engine.priority.result import PriorityResult


def task(**overrides) -> PriorityInput:
    base = dict(
        task_id="TSK-101",
        section_id="SEC-01",
        asset_id="AST-TRK-01",
        criticality="MEDIUM",
        overdue_days=0,
    )
    base.update(overrides)
    return PriorityInput(**base)


def factor(result: PriorityResult, name: str):
    for f in result.factor_scores:
        if f.factor == name:
            return f
    raise AssertionError(f"factor {name} missing from result")


# ---------------------------------------------------------------------------
# Score math (independent recomputation, §20)
# ---------------------------------------------------------------------------


def test_score_is_exact_weighted_sum_of_contributions():
    engine = PriorityEngine()
    result = engine.evaluate(
        task(
            criticality="HIGH",
            overdue_days=10,
            asset_failure_risk=AssetFailureRisk(probability_of_failure=0.4),
            task_type="CORRECTIVE",
            trains_per_day=24,
        )
    )
    expected = sum(f.contribution for f in result.factor_scores)
    assert result.score == pytest.approx(expected, abs=1e-9)
    # Independent recomputation from raw normalized scores × config weights.
    cfg = engine.config
    manual = (
        0.75 * cfg.criticality_weight
        + (10 / 30) * cfg.overdue_weight
        + 0.4 * cfg.failure_risk_weight
        + 0.75 * cfg.safety_task_type_weight_share * cfg.safety_weight
        + (24 / 60) * cfg.downstream_impact_weight
    )
    assert result.score == pytest.approx(manual, abs=1e-9)


def test_contributions_sum_to_score_within_tolerance():
    engine = PriorityEngine()
    result = engine.evaluate(task(criticality="CRITICAL", overdue_days=45))
    assert math.isclose(result.contribution_total, result.score, abs_tol=1e-9)


def test_exposed_weights_sum_to_one():
    engine = PriorityEngine()
    result = engine.evaluate(
        task(
            asset_failure_risk=AssetFailureRisk(probability_of_failure=0.2),
            trains_per_day=10,
            task_type="PREVENTIVE",
        )
    )
    assert result.weight_total == pytest.approx(1.0)


def test_weighted_mean_not_raw_sum_when_weights_renormalised():
    # Config weights sum to 2.0 → engine must normalise them (score ≤ 1).
    engine = PriorityEngine(
        PriorityEngineConfig(
            criticality_weight=0.6,
            overdue_weight=0.4,
            failure_risk_weight=0.4,
            safety_weight=0.4,
            downstream_impact_weight=0.2,
        )
    )
    result = engine.evaluate(
        task(
            criticality="CRITICAL",
            overdue_days=45,
            asset_failure_risk=AssetFailureRisk(probability_of_failure=1.0),
            is_safety_relevant=True,
            trains_per_day=120,
        )
    )
    assert result.score == pytest.approx(1.0)
    assert result.metadata["weights_renormalized"] is True


# ---------------------------------------------------------------------------
# Classification (every class + every boundary, §19)
# ---------------------------------------------------------------------------


def test_classification_thresholds_default_config():
    cfg = PriorityEngineConfig()
    assert classify(0.0, cfg) == "LOW"
    assert classify(0.39, cfg) == "LOW"
    assert classify(0.40, cfg) == "MEDIUM"  # boundary → higher class
    assert classify(0.64, cfg) == "MEDIUM"
    assert classify(0.65, cfg) == "HIGH"
    assert classify(0.84, cfg) == "HIGH"
    assert classify(0.85, cfg) == "CRITICAL"
    assert classify(1.0, cfg) == "CRITICAL"


def test_maximal_input_is_critical():
    engine = PriorityEngine()
    result = engine.evaluate(
        task(
            criticality="CRITICAL",
            overdue_days=45,
            asset_failure_risk=AssetFailureRisk(probability_of_failure=1.0),
            is_safety_relevant=True,
            trains_per_day=120,
        )
    )
    assert result.score == pytest.approx(1.0)
    assert result.priority_class == "CRITICAL"


def test_minimal_input_is_low():
    engine = PriorityEngine()
    result = engine.evaluate(
        task(
            criticality="LOW",
            overdue_days=0,
            asset_failure_risk=AssetFailureRisk(probability_of_failure=0.0),
            is_safety_relevant=False,
            trains_per_day=0,
        )
    )
    assert result.score == pytest.approx(0.25 * 0.30)  # only criticality contributes
    assert result.priority_class == "LOW"


def test_configurable_thresholds_change_classification():
    cfg = PriorityEngineConfig(threshold_medium=0.20, threshold_high=0.50, threshold_critical=0.60)
    assert classify(0.075, cfg) == "LOW"   # below the raised medium threshold
    assert classify(0.20, cfg) == "MEDIUM"  # boundary → higher class
    engine = PriorityEngine(cfg)
    result = engine.evaluate(task(criticality="MEDIUM"))  # 0.50 → MEDIUM
    assert result.priority_class == "MEDIUM"
    high = engine.evaluate(task(criticality="CRITICAL"))  # 1.0 ≥ 0.60
    assert high.priority_class == "CRITICAL"


# ---------------------------------------------------------------------------
# Weighting behaviour (§19)
# ---------------------------------------------------------------------------


def test_weight_change_moves_score():
    high_crit = PriorityEngineConfig(criticality_weight=0.9, overdue_weight=0.02, failure_risk_weight=0.02, safety_weight=0.03, downstream_impact_weight=0.03)
    low_crit = PriorityEngineConfig(criticality_weight=0.1, overdue_weight=0.225, failure_risk_weight=0.225, safety_weight=0.225, downstream_impact_weight=0.225)
    t = task(criticality="CRITICAL", overdue_days=20)
    s_high_crit = PriorityEngine(high_crit).evaluate(t).score
    s_low_crit = PriorityEngine(low_crit).evaluate(t).score
    assert s_high_crit > s_low_crit


def test_zero_weight_factor_has_zero_contribution_but_is_reported():
    cfg = PriorityEngineConfig(downstream_impact_weight=0.0)
    engine = PriorityEngine(cfg)
    result = engine.evaluate(task(trains_per_day=60))
    f = factor(result, "downstream_impact")
    assert f.weight == 0.0
    assert f.contribution == 0.0
    assert "downstream_impact" in [z for z in result.explanation.split("Zero-weight factors: ")[-1].split(".")[0].split(", ")]


def test_zero_weight_absent_factor_does_not_renormalise_others():
    # With EXCLUDE policy, an absent AND zero-weight factor is simply absent.
    cfg = PriorityEngineConfig(downstream_impact_weight=0.0)
    engine = PriorityEngine(cfg)
    result = engine.evaluate(task())  # no trains_per_day → absent
    assert result.weight_total == pytest.approx(1.0)
    assert all(f.factor != "downstream_impact" for f in result.factor_scores)


# ---------------------------------------------------------------------------
# Missing data (every policy, §19)
# ---------------------------------------------------------------------------


def test_exclude_policy_reports_missing_factors():
    engine = PriorityEngine()  # default EXCLUDE_FACTOR
    result = engine.evaluate(task())
    assert set(result.missing_factors) == {"failure_risk", "safety", "downstream_impact"}
    assert "excluded" in result.explanation
    assert result.weight_total == pytest.approx(1.0)


def test_exclude_policy_renormalises_to_known_factors():
    engine = PriorityEngine()
    result = engine.evaluate(task(trains_per_day=60))  # only downstream missing… actually supply all but risk
    weights = {f.factor: f.weight for f in result.factor_scores}
    total = sum(weights.values())
    assert total == pytest.approx(1.0)
    # criticality keeps its relative dominance among present factors
    assert weights["criticality"] == max(weights.values())


def test_zero_policy_keeps_full_weight_and_scores_zero():
    engine = PriorityEngine(PriorityEngineConfig(missing_data_policy=MissingDataPolicy.ZERO))
    result = engine.evaluate(task())
    assert result.missing_factors == []
    assert len(result.factor_scores) == 5
    f = factor(result, "failure_risk")
    assert f.normalized_score == 0.0
    assert f.weight == pytest.approx(0.20)
    assert "scored 0.0" in result.explanation


def test_required_factor_missing_is_a_construction_error():
    with pytest.raises(Exception):
        PriorityInput(task_id="T", section_id="SEC-01", criticality="HIGH")  # overdue_days absent
    with pytest.raises(Exception):
        PriorityInput(task_id="T", section_id="SEC-01", overdue_days=0)  # criticality absent


def test_unknown_criticality_rejected():
    with pytest.raises(Exception):
        PriorityInput(task_id="T", section_id="SEC-01", criticality="CATASTROPHIC", overdue_days=0)


# ---------------------------------------------------------------------------
# Deadline / time pressure semantics
# ---------------------------------------------------------------------------


def test_overdue_is_the_time_pressure_factor():
    """The spec has no separate deadline factor; overdue days carries urgency."""
    engine = PriorityEngine()
    fresh = engine.evaluate(task(overdue_days=0)).score
    due_soon = engine.evaluate(task(overdue_days=5)).score
    late = engine.evaluate(task(overdue_days=30)).score
    assert fresh < due_soon < late


def test_overdue_monotone_with_saturation_cap():
    engine = PriorityEngine()
    s30 = engine.evaluate(task(overdue_days=30)).score
    s60 = engine.evaluate(task(overdue_days=60)).score
    assert s30 == pytest.approx(s60)  # both saturate the factor at 1.0


# ---------------------------------------------------------------------------
# Determinism / comparability (§15)
# ---------------------------------------------------------------------------


def test_identical_inputs_produce_identical_results():
    engine = PriorityEngine()
    a = engine.evaluate(
        task(
            criticality="HIGH",
            overdue_days=7,
            asset_failure_risk=AssetFailureRisk(probability_of_failure=0.33),
            task_type="CORRECTIVE",
            trains_per_day=30,
        )
    )
    b = engine.evaluate(
        task(
            criticality="HIGH",
            overdue_days=7,
            asset_failure_risk=AssetFailureRisk(probability_of_failure=0.33),
            task_type="CORRECTIVE",
            trains_per_day=30,
        )
    )
    assert a.model_dump() == b.model_dump()


def test_score_is_bounded_0_1():
    engine = PriorityEngine()
    lo = engine.evaluate(task(criticality="LOW", overdue_days=0, is_safety_relevant=False, trains_per_day=0))
    hi = engine.evaluate(
        task(criticality="CRITICAL", overdue_days=99, asset_failure_risk=AssetFailureRisk(probability_of_failure=1.0), is_safety_relevant=True, trains_per_day=999)
    )
    assert 0.0 <= lo.score <= 1.0
    assert 0.0 <= hi.score <= 1.0


def test_monotonicity_in_a_single_factor():
    """For a fixed configuration, raising one factor never lowers the score."""
    engine = PriorityEngine()
    scores = [
        engine.evaluate(task(overdue_days=d, criticality="MEDIUM")).score
        for d in (0, 3, 6, 9, 12, 15)
    ]
    assert scores == sorted(scores)


# ---------------------------------------------------------------------------
# Explainability (§13, §20)
# ---------------------------------------------------------------------------


def test_every_present_factor_is_explained_with_math():
    engine = PriorityEngine()
    result = engine.evaluate(
        task(criticality="HIGH", overdue_days=10, trains_per_day=30, task_type="INSPECTION")
    )
    for f in result.factor_scores:
        assert f.raw_description
        assert 0.0 <= f.normalized_score <= 1.0
        assert f.contribution == pytest.approx(f.normalized_score * f.weight, abs=1e-9)
    assert "normalized" in result.explanation
    assert "weight" in result.explanation


def test_contributing_factors_ordered_by_contribution():
    engine = PriorityEngine()
    result = engine.evaluate(
        task(criticality="CRITICAL", overdue_days=20, trains_per_day=45, task_type="EMERGENCY")
    )
    ordered = result.contributing_factors()
    contributions = [f.contribution for f in ordered]
    assert contributions == sorted(contributions, reverse=True)
    assert ordered[0].factor == "criticality"


def test_explanation_names_the_task_and_class():
    engine = PriorityEngine()
    result = engine.evaluate(task(criticality="CRITICAL", overdue_days=45))
    assert "TSK-101" in result.explanation
    assert result.priority_class in result.explanation


# ---------------------------------------------------------------------------
# Versioning (§13)
# ---------------------------------------------------------------------------


def test_result_carries_version_stamps():
    engine = PriorityEngine()
    result = engine.evaluate(task())
    assert result.engine_version == ENGINE_VERSION == "0.1.0"
    assert result.priority_model_id == PRIORITY_MODEL_ID == "railmind-deterministic-priority"
    assert result.priority_model_version == PRIORITY_MODEL_VERSION == "1.0.0"
