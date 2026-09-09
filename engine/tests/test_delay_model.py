"""E09 tests — §16.3 delay baseline: semantics, exactness, determinism.

The deterministic coefficients (DelayModelConfig defaults) are documented
[ASSUMPTION]s, so tests pin the *formula semantics* (impact → decay →
protection), monotonicity, affinity classification, and validation — not
arbitrary coefficient values where a different documented tuning would be
equally valid.
"""

import math
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from engine.delay import (
    CLASS_CASCADING,
    CLASS_DIRECT,
    CLASS_UNAFFECTED,
    DELAY_ALGORITHM,
    AffectedTrain,
    DelayFeatures,
    DelayModelConfig,
    DelayPredictionResult,
    GraphPropagationDelayModel,
    TrainDelayRecord,
)


def t0():
    return datetime(2026, 9, 14, 22, 0, tzinfo=timezone.utc)


def make_features(**overrides):
    base = dict(
        window_id="W1",
        section_id="S1",
        earliest_start=t0(),
        latest_end=datetime(2026, 9, 15, 2, 0, tzinfo=timezone.utc),
        time_of_day_minutes=1320.0,
        historical_delay_minutes=10.0,
        affected_trains=[
            AffectedTrain(train_id="R1", priority=8.0, route=["S1", "S2"]),
            AffectedTrain(train_id="R2", priority=2.0, route=["S3"]),
            AffectedTrain(train_id="R3", priority=5.0, route=["S4"]),
        ],
        adjacency={"S1": ["S3"], "S3": ["S4"]},
    )
    base.update(overrides)
    return DelayFeatures(**base)


class TestDelaySemantics:
    """§16.3 semantics: direct impact, hop decay, priority protection."""

    def test_direct_train_gets_full_impact_with_protection(self):
        result = GraphPropagationDelayModel().predict(make_features())
        record = next(r for r in result.trains if r.train_id == "R1")
        # impact = 10 × 0.25 = 2.5; protection = 1 − 0.3·(8/10)
        assert record.classification == CLASS_DIRECT
        assert record.propagation_hops == 0
        assert record.delay_minutes == pytest.approx(2.5 * (1 - 0.3 * 0.8))

    def test_cascading_decay_per_hop(self):
        result = GraphPropagationDelayModel().predict(make_features())
        r2 = next(r for r in result.trains if r.train_id == "R2")
        r3 = next(r for r in result.trains if r.train_id == "R3")
        assert r2.classification == CLASS_CASCADING
        assert r2.propagation_hops == 1
        assert r3.propagation_hops == 2
        assert r2.delay_minutes == pytest.approx(2.5 * 0.5 * (1 - 0.3 * 0.2))
        assert r3.delay_minutes == pytest.approx(2.5 * 0.25 * (1 - 0.3 * 0.5))

    def test_monotone_decay_direct_gt_cascading_gt_further(self):
        result = GraphPropagationDelayModel().predict(make_features())
        delays = {r.train_id: r.delay_minutes for r in result.trains}
        assert delays["R1"] > delays["R2"] > delays["R3"] > 0.0

    def test_unreachable_train_is_unaffected_with_zero(self):
        features = make_features(
            affected_trains=[
                AffectedTrain(train_id="RX", priority=5.0, route=["S99"])
            ]
        )
        result = GraphPropagationDelayModel().predict(features)
        record = result.trains[0]
        assert record.classification == CLASS_UNAFFECTED
        assert record.delay_minutes == 0.0

    def test_total_is_sum_of_records(self):
        result = GraphPropagationDelayModel().predict(make_features())
        assert result.total_delay_minutes == pytest.approx(
            sum(r.delay_minutes for r in result.trains)
        )

    def test_zero_historical_delay_zeroes_everything(self):
        result = GraphPropagationDelayModel().predict(
            make_features(historical_delay_minutes=0.0)
        )
        for record in result.trains:
            if record.classification != CLASS_UNAFFECTED:
                assert record.delay_minutes == 0.0
        assert result.total_delay_minutes == 0.0

    def test_higher_priority_means_more_protection(self):
        low = make_features(
            affected_trains=[AffectedTrain(train_id="A", priority=0.0, route=["S1"])]
        )
        high = make_features(
            affected_trains=[AffectedTrain(train_id="A", priority=10.0, route=["S1"])]
        )
        model = GraphPropagationDelayModel()
        d_low = model.predict(low).delay_for("A")
        d_high = model.predict(high).delay_for("A")
        assert d_high < d_low

    def test_confidence_is_configured_constant(self):
        result = GraphPropagationDelayModel().predict(make_features())
        assert result.confidence == DelayModelConfig().baseline_confidence


class TestDelayDeterminism:
    def test_repeated_prediction_identical(self):
        model = GraphPropagationDelayModel()
        a = model.predict(make_features()).model_dump()
        b = model.predict(make_features()).model_dump()
        assert a == b

    def test_record_order_independent_of_input_order(self):
        trains = make_features().affected_trains
        reordered = make_features(affected_trains=list(reversed(trains)))
        a = GraphPropagationDelayModel().predict(make_features())
        b = GraphPropagationDelayModel().predict(reordered)
        assert [r.train_id for r in a.trains] == [r.train_id for r in b.trains]

    def test_algorithm_label_is_honest(self):
        result = GraphPropagationDelayModel().predict(make_features())
        assert result.algorithm == DELAY_ALGORITHM
        assert "deterministic" in result.algorithm

    def test_provenance_identity(self):
        result = GraphPropagationDelayModel().predict(make_features())
        assert result.model_id == "railmind-delay-prediction"
        assert result.model_version == "1.0.0"
        assert result.engine_version


class TestDelayInterface:
    """TRD §17 common model interface conformance."""

    def test_predict_with_uncertainty_matches_predict(self):
        model = GraphPropagationDelayModel()
        features = make_features()
        # §16.3 defines no uncertainty output for the baseline; the method
        # must not fabricate intervals — it returns the deterministic result.
        assert model.predict_with_uncertainty(features).model_dump() == (
            model.predict(features).model_dump()
        )

    def test_explain_is_deterministic_and_structured(self):
        model = GraphPropagationDelayModel()
        features = make_features()
        a = model.explain(features)
        b = model.explain(features)
        assert a == b
        assert a["direct_trains"] == ["R1"]
        assert a["cascading_trains"][0]["hops"] == 1

    def test_get_version_is_deterministic_string(self):
        assert GraphPropagationDelayModel().get_version()


class TestDelayValidation:
    """§7/§21: loud rejection, never silent defaults."""

    def test_empty_train_id_rejected(self):
        with pytest.raises(ValidationError):
            AffectedTrain(train_id="", priority=1.0, route=["S1"])

    def test_negative_priority_rejected(self):
        with pytest.raises(ValidationError):
            AffectedTrain(train_id="R", priority=-1.0, route=["S1"])

    def test_nan_historical_delay_rejected(self):
        with pytest.raises(ValidationError):
            make_features(historical_delay_minutes=float("nan"))

    def test_infinite_time_of_day_rejected(self):
        with pytest.raises(ValidationError):
            make_features(time_of_day_minutes=float("inf"))

    def test_time_of_day_out_of_range_rejected(self):
        with pytest.raises(ValidationError):
            make_features(time_of_day_minutes=1440.0)

    def test_inverted_window_bounds_rejected(self):
        with pytest.raises(ValidationError):
            make_features(
                earliest_start=t0(),
                latest_end=datetime(2026, 9, 14, 21, 0, tzinfo=timezone.utc),
            )

    def test_duplicate_train_ids_rejected(self):
        with pytest.raises(ValidationError):
            make_features(
                affected_trains=[
                    AffectedTrain(train_id="R", priority=1.0, route=["S1"]),
                    AffectedTrain(train_id="R", priority=2.0, route=["S1"]),
                ]
            )

    def test_empty_route_entry_rejected(self):
        with pytest.raises(ValidationError):
            AffectedTrain(train_id="R", priority=1.0, route=[""])

    def test_negative_historical_delay_rejected(self):
        with pytest.raises(ValidationError):
            make_features(historical_delay_minutes=-0.5)


class TestDelayConfig:
    def test_propagation_factor_must_decay(self):
        with pytest.raises(ValidationError):
            DelayModelConfig(propagation_factor=1.0)

    def test_depth_lower_bound(self):
        with pytest.raises(ValidationError):
            DelayModelConfig(max_propagation_depth=0)

    def test_attenuation_bounds(self):
        with pytest.raises(ValidationError):
            DelayModelConfig(priority_attenuation=1.5)

    def test_serialization_round_trip(self):
        result = GraphPropagationDelayModel().predict(make_features())
        restored = DelayPredictionResult.model_validate_json(result.model_dump_json())
        assert restored == result


class TestDelayRecords:
    def test_record_frozen(self):
        record = TrainDelayRecord(
            train_id="R", classification=CLASS_DIRECT, delay_minutes=1.0
        )
        with pytest.raises(ValidationError):
            record.delay_minutes = 2.0

    def test_all_record_fields_finite(self):
        result = GraphPropagationDelayModel().predict(make_features())
        for record in result.trains:
            assert math.isfinite(record.delay_minutes)
            assert 0.0 <= record.priority_protection_factor <= 1.0
