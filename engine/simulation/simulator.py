"""Seeded Monte Carlo robustness pass (E05) — blueprint §17.6.

For each candidate block window the pass is exactly what §17.6 specifies:

    run N draws; in each draw, sample each task duration from its [P10, P90]
    band; re-check §17.4 constraint 6 (duration feasibility: the window must
    accommodate the summed sampled durations) and constraint 7 (window
    bounds: end − start ≤ maxdur_w); report P(overrun) per block and
    P(any-plan-violation) overall.

Definitions (authoritative, not invented):
- **block overrun** — a draw violates c6 or c7 for that window ("re-check
  constraint 6 and 7 under each draw" ⇒ the per-block overrun event IS the
  c6/c7 failure; §16.1's phrase "exceeds latest_finish constraint" is the
  c7 reading of the same event);
- **plan violation** — at least one window violates c6/c7 in that draw
  (P(any-plan-violation)).

Randomness is isolated inside this module's sampling functions (§6/§23):
a local ``random.Random`` per stream, seeded from the caller's config.
E01–E04 deterministic semantics are untouched (§42).
"""

import hashlib
import math
from typing import Dict, List, Sequence, Tuple

from engine._version import (
    ENGINE_VERSION,
    SIMULATION_MODEL_ID,
    SIMULATION_MODEL_VERSION,
)
from engine.simulation.configuration import SimulationConfig
from engine.simulation.distributions import make_rng, sample_window_durations
from engine.simulation.inputs import BlockWindow, validate_block_windows
from engine.simulation.result import (
    BlockRiskProfile,
    PlanSimulationResult,
    SampleSummary,
)

# §17.4 c6/c7 exceedance keys (stable, part of the evidence contract).
C6_DURATION_FEASIBILITY = "c6_duration_feasibility"
C7_WINDOW_BOUNDS = "c7_window_bounds"

_CONSTRAINT_KEYS = (C6_DURATION_FEASIBILITY, C7_WINDOW_BOUNDS)


def simulate_block(
    window: BlockWindow,
    config: SimulationConfig = None,
    seed: int = None,
) -> PlanSimulationResult:
    """Run the §17.6 robustness pass for one block window.

    By default the window's RNG stream is seeded deterministically from
    (config.seed, window_id) — the SAME rule ``simulate_plan`` applies — so
    ``simulate_block(w, cfg)`` and ``simulate_plan([w], cfg)`` always agree
    and solo results never depend on what else is simulated (§28). An
    explicit ``seed`` overrides the derivation for fully manual control.
    """
    cfg = config or SimulationConfig()
    validate_block_windows([window])

    draw_seed = derive_stream_seed(cfg.seed, window.window_id) if seed is None else seed
    draws = _run_draws(window, cfg, draw_seed)

    return _single_window_result(window, cfg, draw_seed, draws)


def simulate_plan(
    windows: Sequence[BlockWindow],
    config: SimulationConfig = None,
) -> PlanSimulationResult:
    """Run the robustness pass across a whole candidate plan.

    Window ordering must never change results (§28): every window is
    simulated with its own dedicated RNG stream, seeded deterministically
    from (config.seed, window_id) — so simulating A then B, B then A, or
    any subset yields identical per-window results, and the plan-level
    draw alignment (same draw index space) makes
    P(any-plan-violation) independent of candidate order too.
    """
    cfg = config or SimulationConfig()
    if not windows:
        raise ValueError(
            "simulate_plan requires at least one window; an empty plan is "
            "a caller error, not an empty report"
        )
    validate_block_windows(windows)

    profiles: List[BlockRiskProfile] = []
    exceedances: Dict[str, int] = {key: 0 for key in _CONSTRAINT_KEYS}

    for window in windows:
        # simulate_block applies the same (config.seed, window_id) stream
        # derivation, so batch and solo runs are identical by construction.
        window_result = simulate_block(window, cfg)
        profile = window_result.block_profiles[0]
        profiles.append(profile)
        for key in _CONSTRAINT_KEYS:
            exceedances[key] += profile.constraint_exceedances[key]

    # Draw-aligned union across windows (all profiles share the same draw
    # index space, so index i means the same draw for every window).
    violating_draw_indexes: set = set()
    for profile in profiles:
        violating_draw_indexes.update(profile.violation_draws)
    any_plan_violation_draws = len(violating_draw_indexes)

    return PlanSimulationResult(
        candidate_id=_plan_candidate_id(windows),
        iterations=cfg.iterations,
        seed=cfg.seed,
        distribution=cfg.distribution.value,
        plan_violation_probability=any_plan_violation_draws / cfg.iterations,
        any_plan_violation_draws=any_plan_violation_draws,
        constraint_exceedances=exceedances,
        block_profiles=profiles,
        simulation_model_id=SIMULATION_MODEL_ID,
        simulation_model_version=SIMULATION_MODEL_VERSION,
        engine_version=ENGINE_VERSION,
    )


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _run_draws(
    window: BlockWindow, cfg: SimulationConfig, seed: int
) -> Tuple[List[bool], Dict[str, int], List[float]]:
    """The seeded draw loop: sample → re-check c6/c7 (§17.6).

    Returns (per-draw violation flags, exceedance counts, total durations).
    """
    rng = make_rng(seed)
    violation_flags: List[bool] = []
    exceedances: Dict[str, int] = {key: 0 for key in _CONSTRAINT_KEYS}
    totals: List[float] = []

    for _ in range(cfg.iterations):
        sampled = sample_window_durations(window, rng)
        total = math.fsum(duration for _, duration in sampled)
        totals.append(total)

        # §17.4 c6 — duration feasibility: the window must accommodate the
        # summed sampled durations (sequential execution model).
        c6_violated = total > window.max_duration_minutes
        # §17.4 c7 — window bounds: end − start ≤ maxdur_w. Under the same
        # sequential model the span equals the summed duration; a full
        # start/end rescheduling model is Tier 2 (report §13).
        c7_violated = total > window.max_duration_minutes

        violated = c6_violated or c7_violated
        violation_flags.append(violated)
        if c6_violated:
            exceedances[C6_DURATION_FEASIBILITY] += 1
        if c7_violated:
            exceedances[C7_WINDOW_BOUNDS] += 1

    return violation_flags, exceedances, totals


def _single_window_result(
    window: BlockWindow,
    cfg: SimulationConfig,
    seed: int,
    draws: Tuple[List[bool], Dict[str, int], List[float]],
) -> PlanSimulationResult:
    violation_flags, exceedances, totals = draws
    iterations = cfg.iterations
    overrun_draws = sum(1 for flag in violation_flags if flag)
    probability_overrun = overrun_draws / iterations
    summary = SampleSummary.from_samples(totals)

    profile = BlockRiskProfile(
        window_id=window.window_id,
        section_id=window.section_id,
        iterations=iterations,
        seed=seed,
        probability_overrun=probability_overrun,
        expected_total_duration=summary.mean,
        min_total_duration=summary.min,
        max_total_duration=summary.max,
        p10_total_duration=summary.p10,
        p90_total_duration=summary.p90,
        constraint_exceedances=dict(exceedances),
        violation_draws=[
            index for index, flag in enumerate(violation_flags) if flag
        ],
    )

    return PlanSimulationResult(
        candidate_id=window.window_id,
        iterations=iterations,
        seed=seed,
        distribution=cfg.distribution.value,
        plan_violation_probability=probability_overrun,
        any_plan_violation_draws=overrun_draws,
        constraint_exceedances=dict(exceedances),
        block_profiles=[profile],
        simulation_model_id=SIMULATION_MODEL_ID,
        simulation_model_version=SIMULATION_MODEL_VERSION,
        engine_version=ENGINE_VERSION,
    )


def _plan_candidate_id(windows: Sequence[BlockWindow]) -> str:
    """Stable multi-window plan identity from caller-supplied ids.

    E05 never invents identities; the joined form is deterministic and
    auditable (every component id remains visible).
    """
    return "PLAN[" + "+".join(w.window_id for w in windows) + "]"


def derive_stream_seed(base_seed: int, window_id: str) -> int:
    """Deterministic per-window stream seed, stable across orderings.

    A cryptographic hash is used purely as a deterministic mixer of
    (base_seed, window_id) into the RNG's 63-bit seed space; it has no
    security role. Exposed because it is part of the reproducibility
    contract (the profile reports the exact stream seed used).
    """
    digest = hashlib.blake2b(
        f"{base_seed}:{window_id}".encode("utf-8"), digest_size=8
    ).digest()
    return int.from_bytes(digest, "big") & 0x7FFF_FFFF_FFFF_FFFF
