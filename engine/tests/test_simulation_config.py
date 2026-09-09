"""Tests — E05 configuration: authoritative defaults and strict validation."""

import pytest
from pydantic import ValidationError

from engine.simulation.configuration import DurationDistribution, SimulationConfig
from engine.simulation.inputs import BlockWindow, DurationBand


# --- §35 #1-2: defaults and valid iterations --------------------------------


def test_default_configuration_matches_authoritative_spec():
    cfg = SimulationConfig()
    assert cfg.iterations == 200          # blueprint §17.6 / TRD §26 / TRD §34
    assert cfg.distribution == DurationDistribution.UNIFORM
    assert isinstance(cfg.seed, int) and cfg.seed >= 0


@pytest.mark.parametrize("n", [1, 2, 200, 10_000])
def test_valid_iteration_counts_accepted(n):
    assert SimulationConfig(iterations=n).iterations == n


# --- §35 #3: invalid iteration counts rejected, never defaulted -------------


@pytest.mark.parametrize("bad", [0, -1, -200])
def test_non_positive_iterations_rejected(bad):
    with pytest.raises(ValidationError, match="iterations must be >= 1"):
        SimulationConfig(iterations=bad)


def test_non_integer_iterations_rejected():
    with pytest.raises(ValidationError):
        SimulationConfig(iterations=12.5)  # type: ignore[arg-type]
    with pytest.raises(ValidationError):
        SimulationConfig(iterations="many")  # type: ignore[arg-type]


# --- §35 #4: valid seeds; negative seeds rejected ---------------------------


@pytest.mark.parametrize("seed", [0, 1, 42, 2**63 - 1])
def test_valid_seeds_accepted(seed):
    assert SimulationConfig(seed=seed).seed == seed


def test_negative_seed_rejected():
    with pytest.raises(ValidationError):
        SimulationConfig(seed=-1)


# --- distribution is the documented least-assumptive choice -----------------


def test_only_the_documented_distribution_exists():
    # §10: no invented distributions. The single supported shape is explicit.
    assert [m.value for m in DurationDistribution] == ["UNIFORM"]


# --- §35 #5-7: duration/window parameter validation -------------------------


def test_band_p10_above_p90_rejected_not_reordered():
    with pytest.raises(ValidationError, match="p10_minutes"):
        DurationBand(task_id="T1", p10_minutes=50.0, p90_minutes=30.0)


@pytest.mark.parametrize("bad", [0.0, -5.0])
def test_band_non_positive_bounds_rejected(bad):
    with pytest.raises(ValidationError):
        DurationBand(task_id="T1", p10_minutes=bad, p90_minutes=40.0)
    with pytest.raises(ValidationError):
        DurationBand(task_id="T1", p10_minutes=30.0, p90_minutes=bad)


def test_equal_p10_p90_is_a_degenerate_but_valid_band():
    band = DurationBand(task_id="T1", p10_minutes=40.0, p90_minutes=40.0)
    assert band.p10_minutes == band.p90_minutes == 40.0


def test_window_bounds_must_be_ordered():
    from datetime import datetime, timezone

    start = datetime(2026, 9, 14, 22, 0, tzinfo=timezone.utc)
    end = datetime(2026, 9, 15, 2, 0, tzinfo=timezone.utc)
    with pytest.raises(ValidationError, match="latest_end"):
        BlockWindow(
            window_id="W", section_id="S", earliest_start=end,
            latest_end=start, max_duration_minutes=60.0,
        )


def test_window_non_positive_max_duration_rejected():
    from datetime import datetime, timezone

    start = datetime(2026, 9, 14, 22, 0, tzinfo=timezone.utc)
    end = datetime(2026, 9, 15, 2, 0, tzinfo=timezone.utc)
    with pytest.raises(ValidationError):
        BlockWindow(
            window_id="W", section_id="S", earliest_start=start,
            latest_end=end, max_duration_minutes=0.0,
        )
