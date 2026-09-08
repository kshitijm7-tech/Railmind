"""Engine configuration (constraint §20: business values are configuration).

Default values follow the authoritative project defaults — objective weight
defaults are blueprint §17.5 [ASSUMPTION] values and Monte Carlo counts are
TRD §65 planning defaults — but E01 uses only the feasibility-side values.
"""

from pydantic import BaseModel, ConfigDict


class ConstraintEngineConfig(BaseModel):
    """Business configuration for constraint evaluation."""

    model_config = ConfigDict(frozen=True)

    # Minimum useful maintenance block length in minutes (blocks shorter than
    # this are flagged; 0 disables the check).
    minimum_block_minutes: float = 0.0

    # Preferred maintenance window (soft rule): night possession pattern,
    # blueprint §12 — "night-heavy, consistent with typical possession patterns".
    preferred_window_start_hour: int = 22
    preferred_window_end_hour: int = 6

    # Workload-balance soft rule tolerance: deviation from the average per-
    # section maintenance load (minutes) allowed before a warning.
    workload_balance_tolerance_percent: float = 25.0

    # Train-impact soft rule: scheduled trains passing within this many minutes
    # of the block interval (on the block's section) raise a proximity warning.
    train_impact_buffer_minutes: float = 15.0
