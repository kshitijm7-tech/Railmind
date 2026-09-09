"""Simulation configuration (E05) — blueprint §17.6 / TRD §26 / config §34.

The Tier-1 robustness pass is a *simplified* Monte Carlo, explicitly scoped
by the authoritative specification:

- **Iterations**: N=200 draws (blueprint §17.6; TRD §26 "N = 200 simulations";
  TRD §34 config `simulation.monte_carlo_runs: 200`). Configuration value,
  not a hard-coded constant.
- **Sampling**: each task duration is sampled from its **[P10, P90] band**
  (§17.6; PRD §30 "the configured uncertainty range").
- **Checks**: re-check §17.4 constraints **6 (duration feasibility)** and
  **7 (window bounds)** under each draw.
- **Outputs**: P(overrun) per block and P(any-plan-violation) overall.

The distribution *shape* over the [P10, P90] band is deliberately NOT
specified by the documents. E05 therefore defaults to the least-assumptive
choice — a uniform distribution over the band — and validates any
alternative strictly (no invented distributions).
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DurationDistribution(str, Enum):
    """Distribution used to draw durations from the [P10, P90] band.

    ``UNIFORM`` is the E05 default: the specification mandates the band but
    is silent on the shape, so the least-assumptive choice is encoded and
    documented. No other shapes are invented (report §4).
    """

    UNIFORM = "UNIFORM"


class SimulationConfig(BaseModel):
    """Seeded Monte Carlo robustness-pass settings (all validated)."""

    model_config = ConfigDict(frozen=True)

    iterations: int = Field(
        default=200,
        description="Monte Carlo draws (blueprint §17.6 / TRD §26: N=200).",
    )
    seed: int = Field(
        default=0,
        ge=0,
        description="Explicit deterministic seed; never implicit system entropy.",
    )
    distribution: DurationDistribution = DurationDistribution.UNIFORM

    @field_validator("iterations")
    @classmethod
    def _iterations_positive(cls, value: int) -> int:
        # §9: invalid iteration counts are rejected, never silently defaulted.
        # The spec's floor is N=1 ("run N=200" is the Tier-1 default, not the
        # minimum); N=0 would make every probability a division by zero (§22).
        if value < 1:
            raise ValueError(
                f"iterations must be >= 1 (a zero-draw simulation cannot "
                f"produce a probability); got {value}"
            )
        return value
