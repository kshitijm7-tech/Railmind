"""Simulation inputs (E05) — P10/P90 duration bands and §17.4 c6/c7 windows.

All inputs are frozen value objects validated for finiteness and domain
bounds (§21). E05 consumes upstream identifiers verbatim; it never
reconstructs priorities (E02) or objective values (E03).

- ``DurationBand``: [P10, P90] per task — the authoritative uncertainty band
  (§17.6). ``p10`` is the 10th-percentile duration; ``p90`` the 90th. The
  deterministic expected duration stays upstream (E03/task data) and is
  never overwritten by sampling (§11).
- ``BlockWindow``: the candidate block being simulated, with the §17.4 c7
  window bounds [earliest_start, latest_end] and ``max_duration_minutes``
  against which sampled durations are re-checked.
"""

import math
from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _finite(value: float, name: str) -> float:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite; got {value!r}")
    return value


class DurationBand(BaseModel):
    """[P10, P90] duration uncertainty band for one task (§17.6)."""

    model_config = ConfigDict(frozen=True)

    task_id: str
    p10_minutes: float = Field(gt=0.0)
    p90_minutes: float = Field(gt=0.0)

    @field_validator("p10_minutes", "p90_minutes")
    @classmethod
    def _finite_positive(cls, value: float, info) -> float:
        _finite(value, info.field_name)
        if value <= 0.0:
            raise ValueError(
                f"{info.field_name} must be positive; got {value!r} "
                "(durations are magnitudes)"
            )
        return value

    @model_validator(mode="after")
    def _p10_le_p90(self) -> "DurationBand":
        # §24: validate parameter relationships; never silently reorder.
        if self.p10_minutes > self.p90_minutes:
            raise ValueError(
                f"task {self.task_id!r}: p10_minutes ({self.p10_minutes}) "
                f"must be <= p90_minutes ({self.p90_minutes})"
            )
        return self


class BlockWindow(BaseModel):
    """One candidate block window under simulation (§17.3 y[w] + c6/c7)."""

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    window_id: str
    section_id: str
    # §17.4 c7 window bounds.
    earliest_start: datetime
    latest_end: datetime
    max_duration_minutes: float = Field(gt=0.0)
    # Tasks assigned to this window with their P10/P90 bands.
    task_bands: List[DurationBand] = []

    @field_validator("window_id", "section_id")
    @classmethod
    def _ids_nonempty(cls, value: str, info) -> str:
        if not value or not value.strip():
            raise ValueError(f"{info.field_name} must be non-empty")
        return value

    @field_validator("max_duration_minutes")
    @classmethod
    def _finite_max_duration(cls, value: float, info) -> float:
        _finite(value, info.field_name)
        if value <= 0.0:
            raise ValueError(f"{info.field_name} must be positive; got {value!r}")
        return value

    @model_validator(mode="after")
    def _window_bounds_ordered(self) -> "BlockWindow":
        if self.latest_end <= self.earliest_start:
            raise ValueError(
                f"window {self.window_id!r}: latest_end must be strictly "
                "after earliest_start"
            )
        return self


def validate_block_windows(windows) -> None:
    """§21 boundary defense: reject NaN/±inf/invalid bounds loudly.

    Per-window structural validation happens in ``BlockWindow``; this guard
    also rejects duplicate window ids (ambiguous per-block reporting).
    """
    seen = set()
    for window in windows:
        for name in ("max_duration_minutes",):
            _finite(getattr(window, name), name)
        for band in window.task_bands:
            _finite(band.p10_minutes, "p10_minutes")
            _finite(band.p90_minutes, "p90_minutes")
        if window.window_id in seen:
            raise ValueError(
                f"duplicate window_id {window.window_id!r} — per-block "
                "reporting requires unique identities"
            )
        seen.add(window.window_id)
