"""Seeded Monte Carlo sampling (E05) — the explicit randomness boundary.

The ONLY random-number generation in the engine lives in this module.
Everything else in RailMind's engine layer remains deterministic (E01–E04).

Isolation rules (E05 §6/§23):
- a local ``random.Random(seed)`` instance — the global RNG state is never
  touched, so engine-wide behavior is unaffected;
- the seed comes exclusively from the caller's ``SimulationConfig``;
- identical (config, seed, inputs) → identical samples (§8).

Distribution: uniform over the caller's [P10, P90] band — the least-
assumptive reading of the spec's "sampling each dur_t from its [P10, P90]
band" (§17.6), which mandates the band but is silent on the shape.
"""

import random
from typing import List, Tuple

from engine.simulation.inputs import DurationBand


def make_rng(seed: int) -> random.Random:
    """A dedicated local RNG instance (never the global ``random`` state)."""
    return random.Random(seed)


def sample_duration(band: DurationBand, rng: random.Random) -> float:
    """One uniform draw within the task's [P10, P90] band."""
    return rng.uniform(band.p10_minutes, band.p90_minutes)


def sample_window_durations(
    window, rng: random.Random
) -> List[Tuple[str, float]]:
    """One draw per task in the window, in the window's stable task order.

    Deterministic given (task order, band parameters, rng state): the task
    order is the caller-supplied ``task_bands`` order, which E05 treats as
    contractually stable.
    """
    return [
        (band.task_id, sample_duration(band, rng))
        for band in window.task_bands
    ]
