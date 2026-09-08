"""Monte Carlo result contracts (E05).

Immutable, serializable results carrying the §17.6 metrics, the sampling
evidence behind them (iterations/seed/distribution/threshold/exceedance
counts) and the upstream candidate linkage (§14). Provenance E02→E03→E04
lineage is not overwritten: E05 adds its own model identity to results that
reference candidate ids supplied by the caller.
"""

import math
from typing import Dict, List

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# Nearest-rank percentile indexes are computed in SampleSummary; keep the
# method explicit so results are reproducible and auditable.
_PERCENTILE_METHOD = "nearest-rank on sorted draws"


class SampleSummary(BaseModel):
    """Summary statistics over the per-draw total sampled durations."""

    model_config = ConfigDict(frozen=True)

    count: int = Field(ge=1)
    min: float
    max: float
    mean: float
    p10: float
    p90: float
    percentile_method: str = _PERCENTILE_METHOD

    @field_validator("min", "max", "mean", "p10", "p90")
    @classmethod
    def _finite(cls, value: float, info) -> float:
        if not math.isfinite(value):
            raise ValueError(f"{info.field_name} must be finite; got {value!r}")
        return value

    @classmethod
    def from_samples(cls, samples: List[float]) -> "SampleSummary":
        """Deterministic summary via nearest-rank percentiles (§25).

        A zero-sample list is impossible here: the config boundary rejects
        iterations < 1 (§22).
        """
        if not samples:
            raise ValueError("cannot summarize an empty sample list")
        ordered = sorted(samples)
        n = len(ordered)

        def nearest_rank(fraction: float) -> float:
            index = max(0, math.ceil(fraction * n) - 1)
            return ordered[index]

        return cls(
            count=n,
            min=ordered[0],
            max=ordered[-1],
            mean=math.fsum(ordered) / n,
            p10=nearest_rank(0.10),
            p90=nearest_rank(0.90),
        )


class BlockRiskProfile(BaseModel):
    """Per-block §17.6 evidence: P(overrun) plus the numbers behind it."""

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    window_id: str
    section_id: str
    iterations: int = Field(ge=1)
    seed: int = Field(ge=0)
    probability_overrun: float = Field(ge=0.0, le=1.0)
    expected_total_duration: float
    min_total_duration: float
    max_total_duration: float
    p10_total_duration: float
    p90_total_duration: float
    # §17.4 c6/c7 exceedance counts over all draws (empirical evidence).
    constraint_exceedances: Dict[str, int] = {}
    # Draw indexes whose c6/c7 check failed (auditable, reproducible).
    violation_draws: List[int] = []


class PlanSimulationResult(BaseModel):
    """§17.6 robustness-pass result for a block or a whole candidate plan."""

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    # Candidate linkage (§14): caller-supplied E04 candidate/window identity.
    candidate_id: str
    iterations: int = Field(ge=1)
    seed: int = Field(ge=0)
    distribution: str

    # Aggregate §17.6 outputs.
    # Per-window probability_overrun and overall P(any-plan-violation):
    plan_violation_probability: float = Field(ge=0.0, le=1.0)
    any_plan_violation_draws: int = Field(ge=0)
    # Σ over windows of per-window c6/c7 exceedance counts.
    constraint_exceedances: Dict[str, int] = {}

    block_profiles: List[BlockRiskProfile] = []

    # E05 provenance (upstream E02/E03/E04 lineage is referenced through the
    # candidate_id and never rewritten here).
    simulation_model_id: str
    simulation_model_version: str
    engine_version: str

    @field_validator("any_plan_violation_draws")
    @classmethod
    def _draws_not_beyond_iterations(cls, value: int, info) -> int:
        # cross-field check happens in model_validator below; this guards
        # the field itself is a sane count.
        return value

    @model_validator(mode="after")
    def _draws_within_iterations(self) -> "PlanSimulationResult":
        if self.any_plan_violation_draws > self.iterations:
            raise ValueError(
                "any_plan_violation_draws cannot exceed iterations"
            )
        return self

    def profile(self, window_id: str) -> BlockRiskProfile:
        """The per-block profile for one window (deterministic lookup)."""
        for block in self.block_profiles:
            if block.window_id == window_id:
                return block
        raise KeyError(f"no block profile for window {window_id!r}")
