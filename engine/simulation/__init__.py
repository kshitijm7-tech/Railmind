"""Scenario Risk Simulation & Uncertainty (E05) — blueprint §17.6.

Seeded Monte Carlo robustness pass: samples task durations from their
[P10, P90] bands, re-checks §17.4 constraints 6 and 7 per draw, and reports
P(overrun) per block and P(any-plan-violation) overall. All randomness is
isolated behind explicit seeds inside this package; E01–E04 deterministic
semantics are untouched.
"""

from engine.simulation.configuration import DurationDistribution, SimulationConfig
from engine.simulation.inputs import BlockWindow, DurationBand, validate_block_windows
from engine.simulation.result import (
    BlockRiskProfile,
    PlanSimulationResult,
    SampleSummary,
)
from engine.simulation.simulator import (
    C6_DURATION_FEASIBILITY,
    C7_WINDOW_BOUNDS,
    simulate_block,
    simulate_plan,
)

__all__ = [
    "SimulationConfig",
    "DurationDistribution",
    "DurationBand",
    "BlockWindow",
    "validate_block_windows",
    "simulate_block",
    "simulate_plan",
    "PlanSimulationResult",
    "BlockRiskProfile",
    "SampleSummary",
    "C6_DURATION_FEASIBILITY",
    "C7_WINDOW_BOUNDS",
]
