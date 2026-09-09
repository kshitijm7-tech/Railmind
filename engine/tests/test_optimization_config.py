"""Tests — E03 configuration: §17.5 defaults, validation, weight mapping."""

import pytest
from pydantic import ValidationError

from engine.optimization.configuration import OptimizationConfig


def test_defaults_match_blueprint_17_5_and_trd_25():
    cfg = OptimizationConfig()
    assert cfg.train_delay_weight == pytest.approx(5.0)          # α
    assert cfg.unscheduled_priority_weight == pytest.approx(4.0)  # β
    assert cfg.block_count_weight == pytest.approx(1.0)           # γ
    assert cfg.overrun_risk_weight == pytest.approx(2.0)          # δ
    assert cfg.bundling_weight == pytest.approx(1.0)              # ε


def test_weights_mapping_is_complete_and_ordered():
    mapping = OptimizationConfig().objective_weights()
    assert list(mapping) == [
        "train_delay",
        "unscheduled_priority",
        "block_count",
        "overrun_risk",
        "bundling",
    ]
    assert mapping["train_delay"] == pytest.approx(5.0)
    assert mapping["unscheduled_priority"] == pytest.approx(4.0)


@pytest.mark.parametrize("field", [
    "train_delay_weight",
    "unscheduled_priority_weight",
    "block_count_weight",
    "overrun_risk_weight",
    "bundling_weight",
])
def test_negative_weights_rejected(field):
    with pytest.raises(ValidationError):
        OptimizationConfig(**{field: -1.0})


def test_all_zero_weights_are_configurable_not_hidden():
    # §17.5 does not forbid zero weights (e.g. a pure delay-minimizing run);
    # unlike E02's priority mean, a zero total is representable here because
    # the objective is a weighted SUM, not a weighted mean. Zero weights must
    # simply yield zero components — tested in the objective tests.
    cfg = OptimizationConfig(
        train_delay_weight=0.0,
        unscheduled_priority_weight=0.0,
        block_count_weight=0.0,
        overrun_risk_weight=0.0,
        bundling_weight=0.0,
    )
    assert all(v == 0.0 for v in cfg.objective_weights().values())
