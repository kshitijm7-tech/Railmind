"""Tests — E05 simulation: reproducibility, probability bounds, §17.6 semantics.

Randomness is contractually stable here (explicit seed + stdlib Random), but
tests avoid asserting particular sample values; they assert the invariants
the specification guarantees (§25/§36).
"""

import math
import random as _global_random_module
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from engine._version import (
    ENGINE_VERSION,
    SIMULATION_MODEL_ID,
    SIMULATION_MODEL_VERSION,
)
from engine.simulation.configuration import SimulationConfig
from engine.simulation.distributions import make_rng
from engine.simulation.inputs import BlockWindow, DurationBand
from engine.simulation.result import PlanSimulationResult, SampleSummary
from engine.simulation.simulator import (
    C6_DURATION_FEASIBILITY,
    C7_WINDOW_BOUNDS,
    simulate_block,
    simulate_plan,
)


def band(task_id="T1", p10=30.0, p90=50.0):
    return DurationBand(task_id=task_id, p10_minutes=p10, p90_minutes=p90)


def window(window_id="W1", max_duration=80.0, task_bands=None):
    return BlockWindow(
        window_id=window_id,
        section_id="SEC-1",
        earliest_start=datetime(2026, 9, 14, 22, 0, tzinfo=timezone.utc),
        latest_end=datetime(2026, 9, 15, 2, 0, tzinfo=timezone.utc),
        max_duration_minutes=max_duration,
        task_bands=task_bands if task_bands is not None else [band()],
    )


def cfg(iterations=200, seed=42):
    return SimulationConfig(iterations=iterations, seed=seed)


# ---------------------------------------------------------------------------
# §35 #8 — Reproducibility: same seed + same inputs → same result
# ---------------------------------------------------------------------------


def test_same_seed_and_inputs_produce_identical_results():
    first = simulate_block(window(), cfg())
    second = simulate_block(window(), cfg())
    assert first.model_dump() == second.model_dump()


def test_simulation_result_equality_holds_for_plan_runs():
    first = simulate_plan([window("W1"), window("W2")], cfg())
    second = simulate_plan([window("W1"), window("W2")], cfg())
    assert first.model_dump() == second.model_dump()


# ---------------------------------------------------------------------------
# §35 #9 — Different seeds may differ (and here do, statistically)
# ---------------------------------------------------------------------------


def test_different_seed_can_produce_different_samples():
    # With 200 draws and a genuinely random band, the two streams are
    # expected to differ; assert on the sample paths via violation sets and
    # means, not on a hardcoded sample value.
    a = simulate_block(window(max_duration=78.0), cfg(iterations=200, seed=1))
    b = simulate_block(window(max_duration=78.0), cfg(iterations=200, seed=2))
    # Not a strict requirement (seeds MAY agree by chance), but with 200
    # uniform draws of a 20-minute band, identical summaries are ~impossible.
    assert (
        a.block_profiles[0].violation_draws != b.block_profiles[0].violation_draws
    ) or (
        a.block_profiles[0].expected_total_duration
        != b.block_profiles[0].expected_total_duration
    )


# ---------------------------------------------------------------------------
# §35 #10 — Global RNG state is never mutated (isolation, §23)
# ---------------------------------------------------------------------------


def test_global_random_state_is_untouched():
    before = _global_random_module.getstate()
    rng_a = make_rng(7)
    rng_b = make_rng(7)
    assert [rng_a.random() for _ in range(5)] == [rng_b.random() for _ in range(5)]
    simulate_block(window(), cfg())
    simulate_plan([window("W1"), window("W2")], cfg())
    assert _global_random_module.getstate() == before


# ---------------------------------------------------------------------------
# §35 #11 — P(overrun) always within [0, 1]
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("seed", [0, 1, 42, 999])
def test_probability_overrun_is_always_in_unit_interval(seed):
    result = simulate_block(window(max_duration=78.0), cfg(seed=seed))
    assert 0.0 <= result.plan_violation_probability <= 1.0
    assert 0.0 <= result.block_profiles[0].probability_overrun <= 1.0


# ---------------------------------------------------------------------------
# §35 #12 — Zero-overrun case (wide window vs narrow band)
# ---------------------------------------------------------------------------


def test_zero_overrun_when_window_always_accommodates():
    # Max possible sampled total = 40 + 20 = 60 < 70 ⇒ no draw can violate.
    w = window(
        max_duration=70.0,
        task_bands=[band("T1", 30.0, 40.0), band("T2", 10.0, 20.0)],
    )
    result = simulate_block(w, cfg())
    assert result.plan_violation_probability == pytest.approx(0.0)
    assert result.block_profiles[0].constraint_exceedances[C6_DURATION_FEASIBILITY] == 0
    assert result.block_profiles[0].violation_draws == []


# ---------------------------------------------------------------------------
# §35 #13 — Certain-overrun case (window cannot hold even P10 durations)
# ---------------------------------------------------------------------------


def test_certain_overrun_when_window_never_accommodates():
    # Minimum possible sampled total = 50 + 30 = 80 > 60 ⇒ every draw violates.
    w = window(
        max_duration=60.0,
        task_bands=[band("T1", 50.0, 60.0), band("T2", 30.0, 40.0)],
    )
    result = simulate_block(w, cfg())
    assert result.plan_violation_probability == pytest.approx(1.0)
    profile = result.block_profiles[0]
    assert profile.constraint_exceedances[C6_DURATION_FEASIBILITY] == 200
    assert profile.constraint_exceedances[C7_WINDOW_BOUNDS] == 200


# ---------------------------------------------------------------------------
# §35 #14 — Correct denominator (exceedance counts = iterations at most;
# probability = draws / iterations exactly)
# ---------------------------------------------------------------------------


def test_probability_equals_overrun_draws_over_iterations():
    result = simulate_block(window(max_duration=78.0), cfg(iterations=50, seed=3))
    profile = result.block_profiles[0]
    draws = len(profile.violation_draws)
    assert profile.probability_overrun == pytest.approx(draws / 50)
    # No exceedance count can exceed the iteration count.
    assert all(count <= 50 for count in profile.constraint_exceedances.values())


def test_config_boundary_rejects_zero_iterations_before_any_division():
    with pytest.raises(ValidationError):
        SimulationConfig(iterations=0)


# ---------------------------------------------------------------------------
# §35 #15 — Sampled values obey distribution bounds
# ---------------------------------------------------------------------------


def test_all_sampled_totals_within_band_sum():
    w = window(max_duration=10_000.0, task_bands=[band("T1", 30.0, 50.0), band("T2", 10.0, 25.0)])
    result = simulate_block(w, cfg(iterations=500))
    profile = result.block_profiles[0]
    # Sampled per-task draws are within their bands ⇒ the total is within
    # [sum p10, sum p90] = [40, 75]; the observed min/max must respect that.
    assert profile.min_total_duration >= 40.0
    assert profile.max_total_duration <= 75.0
    assert profile.min_total_duration <= profile.p10_total_duration <= profile.p90_total_duration <= profile.max_total_duration


def test_degenerate_band_yields_exactly_the_band_value():
    w = window(max_duration=100.0, task_bands=[band("T1", 42.0, 42.0)])
    result = simulate_block(w, cfg(iterations=25))
    profile = result.block_profiles[0]
    assert profile.expected_total_duration == pytest.approx(42.0)
    assert profile.min_total_duration == pytest.approx(42.0)
    assert profile.max_total_duration == pytest.approx(42.0)
    assert profile.p10_total_duration == pytest.approx(42.0)
    assert profile.p90_total_duration == pytest.approx(42.0)


# ---------------------------------------------------------------------------
# §35 #16 — Deterministic baseline is not overwritten (§11/§15)
# ---------------------------------------------------------------------------


def test_inputs_remain_unchanged_after_simulation():
    w = window(max_duration=78.0, task_bands=[band("T1"), band("T2", 10.0, 25.0)])
    before = w.model_dump()
    simulate_block(w, cfg())
    simulate_plan([w], cfg())
    assert w.model_dump() == before  # frozen models; E05 never mutates inputs


def test_e05_does_not_touch_e03_or_e04_types():
    """Structural guarantee: the simulator's public surface only consumes
    E05 input models — E03 ObjectiveBreakdown and E04 ScenarioCandidate are
    never modified, rerun, or replaced."""
    import inspect

    import engine.simulation.simulator as sim

    source = inspect.getsource(sim)
    # No objective recomputation (§18) and no priority recomputation (§17).
    for token in (
        "ObjectiveEvaluator",
        "total_train_delay",
        "priority_score",
        "PriorityEngine",
        "ScenarioComparator",
    ):
        assert token not in source, f"E05 duplicates upstream logic: {token!r}"


# ---------------------------------------------------------------------------
# §35 #17 — Expected duration sanity for the known uniform band
# ---------------------------------------------------------------------------


def test_expected_total_converges_to_band_midpoint():
    # E[uniform(a,b)] = (a+b)/2 per task ⇒ 40 + 17.5 = 57.5 for the bands.
    w = window(max_duration=100.0, task_bands=[band("T1", 30.0, 50.0), band("T2", 15.0, 20.0)])
    result = simulate_block(w, cfg(iterations=4000, seed=7))
    assert result.block_profiles[0].expected_total_duration == pytest.approx(57.5, abs=0.5)


# ---------------------------------------------------------------------------
# §26 — Convergence: larger N improves the estimate (statistically)
# ---------------------------------------------------------------------------


def test_convergence_toward_true_midpoint_with_larger_iterations():
    w = window(max_duration=100.0, task_bands=[band("T1", 30.0, 50.0)])
    small = abs(simulate_block(w, cfg(iterations=50, seed=11)).block_profiles[0].expected_total_duration - 40.0)
    large = abs(simulate_block(w, cfg(iterations=5000, seed=11)).block_profiles[0].expected_total_duration - 40.0)
    assert large < small


# ---------------------------------------------------------------------------
# §35 #18-19 — Candidate association and E04 baseline preservation
# ---------------------------------------------------------------------------


def test_candidate_id_is_preserved_verbatim():
    result = simulate_block(window(window_id="CAND-7"), cfg())
    assert result.candidate_id == "CAND-7"
    plan = simulate_plan([window("W-A"), window("W-B")], cfg())
    assert plan.candidate_id == "PLAN[W-A+W-B]"  # deterministic composition


def test_per_window_stream_seed_depends_only_on_base_seed_and_id():
    from engine.simulation.simulator import derive_stream_seed

    assert derive_stream_seed(42, "W1") == derive_stream_seed(42, "W1")
    assert derive_stream_seed(42, "W1") != derive_stream_seed(43, "W1")
    assert derive_stream_seed(42, "W1") != derive_stream_seed(42, "W2")


# ---------------------------------------------------------------------------
# §35 #29-30 — Batch simulation and candidate-order invariance
# ---------------------------------------------------------------------------


def test_batch_plan_simulation_covers_every_window():
    result = simulate_plan(
        [window("W-A", max_duration=80.0), window("W-B", max_duration=60.0)], cfg()
    )
    assert {p.window_id for p in result.block_profiles} == {"W-A", "W-B"}
    # Per-window results identical whether simulated alone or in a batch.
    alone_a = simulate_block(window("W-A", max_duration=80.0), cfg()).block_profiles[0]
    alone_b = simulate_block(window("W-B", max_duration=60.0), cfg()).block_profiles[0]
    batch = {p.window_id: p for p in result.block_profiles}
    assert batch["W-A"] == alone_a
    assert batch["W-B"] == alone_b


def test_window_order_does_not_change_plan_result():
    a, b = window("W-A", max_duration=80.0), window("W-B", max_duration=60.0)
    forward = simulate_plan([a, b], cfg())
    backward = simulate_plan([b, a], cfg())
    # The plan-level draw union and probabilities are order-invariant.
    assert forward.plan_violation_probability == pytest.approx(backward.plan_violation_probability)
    assert forward.any_plan_violation_draws == backward.any_plan_violation_draws
    assert forward.constraint_exceedances == backward.constraint_exceedances
    assert {p.window_id: p for p in forward.block_profiles} == {
        p.window_id: p for p in backward.block_profiles
    }


def test_subset_simulation_is_independent_of_other_windows():
    """Candidate A's simulation must not depend on B being present (§28)."""
    a = window("W-A", max_duration=80.0)
    solo = simulate_plan([a], cfg())
    with_b = simulate_plan([a, window("W-B", max_duration=60.0)], cfg())
    assert solo.block_profiles[0] == dict_to_profile(with_b, "W-A")


def dict_to_profile(plan_result, window_id):
    return {p.window_id: p for p in plan_result.block_profiles}[window_id]


# ---------------------------------------------------------------------------
# §35 #22-28 — Numerical safety at the E05 boundary
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_band_values_rejected(bad):
    with pytest.raises(ValidationError):
        DurationBand(task_id="T1", p10_minutes=bad, p90_minutes=50.0)
    with pytest.raises(ValidationError):
        DurationBand(task_id="T1", p10_minutes=30.0, p90_minutes=bad)


def test_nonfinite_window_max_duration_rejected():
    from datetime import datetime, timezone

    with pytest.raises(ValidationError):
        BlockWindow(
            window_id="W",
            section_id="S",
            earliest_start=datetime(2026, 9, 14, 22, 0, tzinfo=timezone.utc),
            latest_end=datetime(2026, 9, 15, 2, 0, tzinfo=timezone.utc),
            max_duration_minutes=float("nan"),
        )


def test_duplicate_window_ids_rejected_in_batch():
    with pytest.raises(ValueError, match="duplicate window_id"):
        simulate_plan([window("W-DUP"), window("W-DUP")], cfg())


# ---------------------------------------------------------------------------
# §35 #31-32 — Statistical sanity of the empirical overrun estimator
# ---------------------------------------------------------------------------


def test_empirical_overrun_matches_closed_form_for_uniform_sum():
    """Known closed form: T1~U(30,50), T2~U(15,45) independent uniforms;
    P(T1+T2 > 78) = 1 − 455.5/600 ≈ 0.2408. The MC estimate with N=4000
    must land close (σ ≈ 0.0068 ⇒ tolerance 4σ ≈ 0.03 covers MC noise)."""
    w = window(max_duration=78.0, task_bands=[band("T1", 30.0, 50.0), band("T2", 15.0, 45.0)])
    result = simulate_block(w, cfg(iterations=4000, seed=5))
    assert result.plan_violation_probability == pytest.approx(0.2408, abs=0.03)


def test_sample_summary_percentiles_are_ordered_and_in_range():
    w = window(max_duration=100.0, task_bands=[band("T1", 30.0, 50.0)])
    summary = simulate_block(w, cfg(iterations=300)).block_profiles[0]
    assert summary.min_total_duration <= summary.p10_total_duration
    assert summary.p10_total_duration <= summary.p90_total_duration
    assert summary.p90_total_duration <= summary.max_total_duration
    assert summary.min_total_duration >= 30.0
    assert summary.max_total_duration <= 50.0


def test_sample_summary_nearest_rank_known_values():
    summary = SampleSummary.from_samples([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
    assert summary.count == 10
    assert summary.min == 1.0 and summary.max == 10.0
    assert summary.mean == pytest.approx(5.5)
    assert summary.p10 == pytest.approx(1.0)   # ceil(0.1*10)-1 = index 0
    assert summary.p90 == pytest.approx(9.0)   # ceil(0.9*10)-1 = index 8


# ---------------------------------------------------------------------------
# §35 #34 — Serialization round-trip
# ---------------------------------------------------------------------------


def test_simulation_result_serialization_roundtrip():
    result = simulate_plan(
        [window("W-A", max_duration=80.0), window("W-B", max_duration=60.0)],
        cfg(iterations=50, seed=9),
    )
    restored = PlanSimulationResult.model_validate(result.model_dump())
    assert restored.model_dump() == result.model_dump()
    assert restored.simulation_model_id == SIMULATION_MODEL_ID
    assert restored.simulation_model_version == SIMULATION_MODEL_VERSION
    assert restored.engine_version == ENGINE_VERSION


# ---------------------------------------------------------------------------
# §35 #35 — Performance sanity (authoritative N=200 stays fast)
# ---------------------------------------------------------------------------


def test_authoritative_configuration_completes_quickly(benchmark_threshold=5.0):
    import time

    windows = [window(f"W-{i:02d}", max_duration=80.0) for i in range(10)]
    start = time.perf_counter()
    result = simulate_plan(windows, SimulationConfig(iterations=200, seed=42))
    elapsed = time.perf_counter() - start
    assert len(result.block_profiles) == 10
    assert elapsed < benchmark_threshold  # seconds; generous CI-friendly bound
