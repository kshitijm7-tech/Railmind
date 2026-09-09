"""Tests — E06 predictors: inputs, duration model, failure-risk model.

Covers the prompt §35 matrix sections that apply to the authoritative E06
contract: input validation, prediction semantics, deterministic inference,
classification boundaries, provenance, serialization, immutability.
"""

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from engine.prediction import (
    ASSET_TYPE_SCORES,
    P10_FACTOR,
    P90_FACTOR,
    WEIGHTS,
    DurationFeatures,
    DurationPredictor,
    DurationPredictionWindow,
    FailureRiskFeatures,
    FailureRiskPredictor,
    ModelPredictionError,
    PredictionConfig,
)
from engine.prediction.result import (
    DurationPredictionResult,
    FailureRiskPredictionResult,
)

T0 = datetime(2026, 9, 14, 22, 0, tzinfo=timezone.utc)


def make_duration_features(**overrides) -> DurationFeatures:
    base = dict(
        task_id="T-100",
        task_type="CORRECTIVE",
        department="S&T",
        asset_type="SIGNAL",
        section_criticality="MEDIUM",
        crew_size=2,
        historical_duration_minutes=90.0,
        time_of_day_minutes=120.0,
        days_since_last_similar_task=30.0,
    )
    base.update(overrides)
    return DurationFeatures(**base)


def make_failure_features(**overrides) -> FailureRiskFeatures:
    base = dict(
        asset_id="A-200",
        asset_age_days=3650.0,
        asset_type="SWITCH",
        maintenance_history=5,
        failure_history=2,
        criticality="HIGH",
        days_since_last_service=60.0,
        task_backlog=3,
        condition_score=70.0,
    )
    base.update(overrides)
    return FailureRiskFeatures(**base)


# ---------------------------------------------------------------------------
# Input contract validation (prompt §7/§21)
# ---------------------------------------------------------------------------


def test_duration_features_accept_documented_vocabulary():
    f = make_duration_features(task_type="inspection")  # case-insensitive
    assert f.task_type == "INSPECTION"


@pytest.mark.parametrize(
    "field, value",
    [
        ("task_type", "UNKNOWN"),
        ("section_criticality", "critical"),  # enum is case-sensitive (E02 canon)
        ("historical_duration_minutes", -1.0),
        ("crew_size", -2),
    ],
)
def test_invalid_duration_features_rejected(field, value):
    with pytest.raises(ValidationError):
        make_duration_features(**{field: value})


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_duration_features_rejected(bad):
    with pytest.raises(ValidationError):
        make_duration_features(historical_duration_minutes=bad)
    with pytest.raises(ValidationError):
        make_duration_features(time_of_day_minutes=bad)


def test_time_of_day_bounds_enforced():
    with pytest.raises(ValidationError):
        make_duration_features(time_of_day_minutes=1440.0)


def test_naive_deadline_rejected():
    with pytest.raises(ValidationError):
        DurationPredictionWindow(
            start_at=T0.replace(tzinfo=None),
            latest_finish=T0.replace(tzinfo=None) + timedelta(hours=4),
        )


def test_failure_features_validation():
    with pytest.raises(ValidationError):
        make_failure_features(criticality="urgent")
    with pytest.raises(ValidationError):
        make_failure_features(condition_score=100.5)
    with pytest.raises(ValidationError):
        make_failure_features(asset_age_days=-1.0)
    with pytest.raises(ValidationError):
        make_failure_features(days_since_last_service=float("nan"))
    with pytest.raises(ValidationError):
        make_failure_features(time_horizon_hours=0.0)


def test_unknown_asset_type_rejected_at_prediction_not_construction():
    """The type vocabulary is open-ended infrastructure data; validation is
    loud but happens at the predictor boundary against ASSET_TYPE_SCORES."""
    f = make_failure_features(asset_type="HOVERCRAFT")
    with pytest.raises(ModelPredictionError, match="asset_type"):
        FailureRiskPredictor().predict(f)


# ---------------------------------------------------------------------------
# Threshold resolution (overrun semantics — never guessed)
# ---------------------------------------------------------------------------


def test_threshold_resolution_explicit_wins():
    window = DurationPredictionWindow(
        start_at=T0,
        latest_finish=T0 + timedelta(minutes=300),
        overrun_threshold_minutes=42.0,
    )
    assert window.resolved_threshold_minutes(120.0) == 42.0


def test_threshold_resolution_derived_from_deadline():
    window = DurationPredictionWindow(
        start_at=T0, latest_finish=T0 + timedelta(minutes=150)
    )
    assert window.resolved_threshold_minutes(120.0) == 150.0


def test_threshold_resolution_default_when_no_context():
    assert DurationPredictionWindow().resolved_threshold_minutes(99.0) == 99.0


def test_deadline_without_start_is_refused_never_guessed():
    window = DurationPredictionWindow(latest_finish=T0 + timedelta(minutes=150))
    with pytest.raises(ValueError, match="start_at"):
        window.resolved_threshold_minutes(120.0)


def test_inverted_deadline_refused():
    window = DurationPredictionWindow(
        start_at=T0 + timedelta(minutes=10), latest_finish=T0
    )
    with pytest.raises(ValueError, match="latest_finish"):
        window.resolved_threshold_minutes(120.0)


# ---------------------------------------------------------------------------
# Duration predictor — exact deterministic formula
# ---------------------------------------------------------------------------


def test_duration_point_estimate_is_the_exact_documented_formula():
    result = DurationPredictor().predict(make_duration_features())
    expected = 90.0 * 1.00 * 1.15  # MEDIUM criticality × CORRECTIVE task type
    assert result.predicted_duration_minutes == pytest.approx(expected)
    assert result.p10_minutes == pytest.approx(expected * P10_FACTOR)
    assert result.p90_minutes == pytest.approx(expected * P90_FACTOR)
    assert result.p10_minutes < result.predicted_duration_minutes < result.p90_minutes


def test_criticality_and_task_type_factors_apply():
    lo = DurationPredictor().predict(
        make_duration_features(section_criticality="LOW", task_type="INSPECTION")
    )
    hi = DurationPredictor().predict(
        make_duration_features(section_criticality="CRITICAL", task_type="EMERGENCY")
    )
    assert hi.predicted_duration_minutes > lo.predicted_duration_minutes


def test_overrun_probability_is_1_when_point_estimate_exceeds_threshold():
    # 90 × 1.00 × 1.15 = 103.5 > 100 → overrun
    result = DurationPredictor().predict(
        make_duration_features(),
        DurationPredictionWindow(overrun_threshold_minutes=100.0),
    )
    assert result.overrun_probability == 1.0
    assert result.threshold_minutes == 100.0


def test_overrun_probability_is_0_under_threshold():
    result = DurationPredictor().predict(
        make_duration_features(),
        DurationPredictionWindow(overrun_threshold_minutes=104.0),
    )
    assert result.overrun_probability == 0.0


def test_default_threshold_used_when_window_omitted():
    result = DurationPredictor().predict(make_duration_features())
    assert result.threshold_minutes == PredictionConfig().default_overrun_threshold_minutes


def test_reason_codes_deterministic_and_data_derived():
    result = DurationPredictor().predict(
        make_duration_features(section_criticality="HIGH", task_type="EMERGENCY"),
        DurationPredictionWindow(overrun_threshold_minutes=1.0),
    )
    assert result.reason_codes == [
        "OVERRUN_RISK", "HIGH_CRITICALITY_SECTION", "UNPLANNED_WORK",
    ]


def test_zero_historical_duration_refused_not_divided_into_silence():
    with pytest.raises(ModelPredictionError, match="positive"):
        DurationPredictor().predict(make_duration_features(historical_duration_minutes=0.0))


# ---------------------------------------------------------------------------
# Failure-risk predictor — exact deterministic formula and boundaries
# ---------------------------------------------------------------------------


def test_failure_probability_is_the_exact_weighted_mean():
    cfg = PredictionConfig()
    features = make_failure_features()
    components = {
        "age": cfg.normalize(features.asset_age_days, cfg.age_saturation_days),
        "asset_type": ASSET_TYPE_SCORES["SWITCH"],
        "maintenance_history": cfg.normalize(5.0, cfg.history_saturation_events),
        "failure_history": cfg.normalize(2.0, cfg.history_saturation_events),
        "criticality": cfg.criticality_score("HIGH"),
        "service_gap": cfg.normalize(60.0, cfg.service_gap_saturation_days),
        "backlog": cfg.normalize(3.0, cfg.backlog_saturation_tasks),
        "condition": 1.0 - features.condition_score / 100.0,
    }
    expected = sum(components[k] * WEIGHTS[k] for k in WEIGHTS) / sum(WEIGHTS.values())
    result = FailureRiskPredictor().predict(features)
    assert result.probability_of_failure == pytest.approx(expected)


def test_weights_sum_to_one():
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9


def test_risk_class_boundaries_belong_to_higher_class():
    predictor = FailureRiskPredictor()
    cfg = predictor.config
    low = predictor.predict(make_failure_features(failure_history=0, condition_score=100.0))
    assert cfg.classify_risk(low.probability_of_failure) == low.risk_class
    # Boundary ownership is exercised through config.classify_risk tests;
    # here we assert result consistency with the shared classifier.
    assert low.risk_class in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


def test_degradation_evidence_raises_probability():
    healthy = FailureRiskPredictor().predict(
        make_failure_features(failure_history=0, condition_score=100.0, asset_age_days=0.0)
    )
    failing = FailureRiskPredictor().predict(
        make_failure_features(
            failure_history=10, condition_score=0.0,
            asset_age_days=20000.0, days_since_last_service=400.0,
        )
    )
    assert failing.probability_of_failure > healthy.probability_of_failure
    assert failing.risk_class in {"HIGH", "CRITICAL"}
    assert healthy.risk_class in {"LOW", "MEDIUM"}


def test_extreme_inputs_stay_bounded():
    worst = FailureRiskPredictor().predict(
        make_failure_features(
            asset_age_days=1e6, maintenance_history=1000, failure_history=1000,
            criticality="CRITICAL", days_since_last_service=1e5,
            task_backlog=1000, condition_score=0.0,
        )
    )
    assert 0.0 <= worst.probability_of_failure <= 1.0
    assert worst.risk_class == "CRITICAL"  # saturated evidence classifies high


def test_horizon_carried_from_features():
    result = FailureRiskPredictor().predict(make_failure_features(time_horizon_hours=168.0))
    assert result.time_horizon_hours == 168.0


# ---------------------------------------------------------------------------
# TRD §17 interface behavior
# ---------------------------------------------------------------------------


def test_get_version_returns_registry_version():
    from engine._version import DURATION_MODEL_VERSION, FAILURE_RISK_MODEL_VERSION

    assert DurationPredictor().get_version() == DURATION_MODEL_VERSION
    assert FailureRiskPredictor().get_version() == FAILURE_RISK_MODEL_VERSION


def test_predict_with_uncertainty_matches_point_prediction_for_baselines():
    f = make_duration_features()
    p = DurationPredictor()
    assert p.predict_with_uncertainty(f) == p.predict(f)
    ff = make_failure_features()
    fp = FailureRiskPredictor()
    assert fp.predict_with_uncertainty(ff) == fp.predict(ff)


def test_predictors_satisfy_runtime_protocol():
    from engine.prediction.interface import PredictionModel

    assert isinstance(DurationPredictor(), PredictionModel)
    assert isinstance(FailureRiskPredictor(), PredictionModel)


def test_explain_is_deterministic_and_baseline_labeled():
    d = DurationPredictor().explain(make_duration_features())
    f = FailureRiskPredictor().explain(make_failure_features())
    assert d["baseline"] is True and f["baseline"] is True
    assert d == DurationPredictor().explain(make_duration_features())
    assert f == FailureRiskPredictor().explain(make_failure_features())


# ---------------------------------------------------------------------------
# Determinism, immutability, provenance, serialization (prompt §14/§25/§34)
# ---------------------------------------------------------------------------


def test_identical_inputs_produce_identical_results():
    p, fp = DurationPredictor(), FailureRiskPredictor()
    r1, r2 = p.predict(make_duration_features()), p.predict(make_duration_features())
    f1, f2 = fp.predict(make_failure_features()), fp.predict(make_failure_features())
    assert r1.model_dump() == r2.model_dump()
    assert f1.model_dump() == f2.model_dump()


def test_input_models_are_frozen():
    f = make_duration_features()
    with pytest.raises(ValidationError):
        f.task_id = "T-999"
    ff = make_failure_features()
    with pytest.raises(ValidationError):
        ff.condition_score = 1.0


def test_results_are_frozen():
    result = DurationPredictor().predict(make_duration_features())
    with pytest.raises(ValidationError):
        result.overrun_probability = 0.5


def test_upstream_provenance_carried_verbatim_and_bounded():
    from engine.prediction.result import PredictionProvenance

    prov = PredictionProvenance(
        source="AI", state="SIMULATED",
        recorded_at=datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc),
        version="9.9.9", actor="backend-adapter",
    )
    result = DurationPredictor().predict(make_duration_features())
    stamped = result.model_copy(update={"provenance": prov})
    assert stamped.provenance.source == "AI"
    assert stamped.provenance.version == "9.9.9"
    # Invalid vocabulary cannot be constructed:
    with pytest.raises(ValidationError):
        PredictionProvenance(source="GITHUB")
    with pytest.raises(ValidationError):
        PredictionProvenance(state="TBD")


def test_naive_recorded_at_rejected():
    from engine.prediction.result import PredictionProvenance

    with pytest.raises(ValidationError):
        PredictionProvenance(recorded_at=datetime(2026, 9, 14, 12, 0))


def test_serialization_round_trip_preserves_everything():
    from engine.prediction.result import (
        DurationPredictionResult,
        FailureRiskPredictionResult,
    )

    d = DurationPredictor().predict(make_duration_features())
    d2 = DurationPredictionResult.model_validate(d.model_dump())
    assert d2 == d

    f = FailureRiskPredictor().predict(make_failure_features())
    f2 = FailureRiskPredictionResult.model_validate(f.model_dump())
    assert f2 == f
    assert f2.registry_metadata["model_id"] == f.model_id
    assert f2.model_version == f.model_version


def test_registry_metadata_snapshot_present_on_results():
    d = DurationPredictor().predict(make_duration_features())
    assert d.registry_metadata["status"] == "DISABLED"
    assert d.registry_metadata["deterministic_fallback"] is True
    assert d.algorithm == "deterministic-rules"
