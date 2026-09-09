"""Delay-baseline configuration (E09) — documented [ASSUMPTION] constants.

§16.3 specifies the *inputs* and the *model family* (gradient-boosted
regression + NetworkX graph propagation) but no coefficients; no trained
Model 3 artifact exists in the repository (TRD §50/§51). Every coefficient
below is therefore an explicit, validated configuration value — never a
hard-coded magic number — following exactly the E06 baseline's disclosure
discipline. All are exposed so a trained model can replace the baseline
without touching call sites (blueprint §22 swappable-interface rule).
"""

from pydantic import BaseModel, ConfigDict, Field


class DelayModelConfig(BaseModel):
    """Deterministic §16.3 baseline coefficients (documented assumptions)."""

    model_config = ConfigDict(frozen=True)

    # Direct impact: minutes of delay per minute of the section's historical
    # delay summary for a train routed through the blocked section.
    base_direct_factor: float = Field(default=0.25, ge=0.0)
    # Cascading impact: each downstream adjacency hop multiplies the
    # remaining delay by this factor (must be < 1 so propagation decays).
    propagation_factor: float = Field(default=0.5, ge=0.0, lt=1.0)
    # Bound on the propagation pass (§16.3: simple graph-propagation pass —
    # bounded depth keeps the baseline "always finishes on time", §16.4).
    max_propagation_depth: int = Field(default=3, ge=1, le=32)
    # Priority protection: dispatchers re-sequence around high-priority
    # trains, so a train's delay is attenuated by
    # (1 - priority_attenuation × min(priority / priority_scale, 1)).
    priority_attenuation: float = Field(default=0.3, ge=0.0, le=1.0)
    priority_scale: float = Field(default=10.0, gt=0.0)
    # Baseline confidence (§16.3 output "confidence") — constant for the
    # deterministic rules, exactly like E06's baseline predictors.
    baseline_confidence: float = Field(default=0.5, ge=0.0, le=1.0)
