"""Planner configuration (E09) — TRD §65 configuration architecture.

Nothing here may be hard-coded at call sites (TRD §65: "Do not hard-code:
objective weights … solver timeout … Store them in configuration"). The
§17.5 objective weights live in E03's ``OptimizationConfig`` — the planner
reuses that exact contract (single source of truth, no parallel weights) —
and adds only solver-execution settings.
"""

from pydantic import BaseModel, ConfigDict, Field

from engine.optimization.configuration import OptimizationConfig


class PlannerConfig(BaseModel):
    """Solver execution configuration (blueprint §26, TRD §65)."""

    model_config = ConfigDict(frozen=True)

    # TRD §65: optimization.timeout_seconds (§26 Tier-1 target: <10 s full
    # solve). The solver must return inside this budget or report the
    # timeout honestly (never a silently truncated plan).
    timeout_seconds: float = Field(default=10.0, gt=0.0)
    # Number of near-optimal alternatives to return alongside the best plan
    # (TRD §70 DoD: "alternatives generated"; blueprint §21 alternatives).
    alternative_count: int = Field(default=2, ge=0, le=10)
    # TRD §67 reproducibility contract: random_seed is part of every run's
    # identity. CP-SAT is deterministic given (model, seed, workers=1); the
    # seed is recorded in every result.
    random_seed: int = Field(default=0, ge=0)
    # Determinism guard: CP-SAT with multiple workers is nondeterministic in
    # wall-clock; E09 pins single-worker solves (§26: "same seed → same
    # outcome"). Exposed for explicitness, not for callers to flip casually.
    single_worker_deterministic: bool = Field(default=True)
    # E03 owns the §17.5 weights; the planner embeds the same contract.
    objective: OptimizationConfig = Field(default_factory=OptimizationConfig)
