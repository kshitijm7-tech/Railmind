"""Delay-model inputs (E09) — the exact §16.3 feature list.

Blueprint §16.3 input specification: "proposed block window, section,
affected train IDs, train priority, historical delay patterns for the
section, time of day." No invented features, no renames, no speculative
extras — the same discipline as E06's TRD §13/§15 feature vectors.

Caller-supplied canonical data (TRD §36 vocabulary, NetworkX Tier-1):
- each affected train carries its ordered route of sections
  (``routes_through``);
- the section adjacency map carries ``connected_to`` edges, used for the
  downstream/cascading propagation pass.

Affinity contract (documented decision): the caller provides every train it
considers plausibly impacted (direct + downstream). The engine classifies
each train itself — ``direct`` when its route contains the block section,
``cascading`` when its route first reaches a section downstream of the block
section, ``unaffected`` otherwise — so delay semantics never depend on how
the caller pre-filtered the list.
"""

import math
from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _finite(value: float, name: str) -> float:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite; got {value!r}")
    return value


class AffectedTrain(BaseModel):
    """One train exposed to the proposed block (§16.3 affected trains)."""

    model_config = ConfigDict(frozen=True)

    train_id: str
    # §16.3 "train priority". The engine normalizes it against
    # ``DelayModelConfig.priority_scale``; caller-supplied scale.
    priority: float = Field(ge=0.0)
    # §17.1 R: "each train has an ordered route of sections".
    route: List[str] = []

    @field_validator("train_id")
    @classmethod
    def _train_id_nonempty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("train_id must be non-empty")
        return value

    @field_validator("priority")
    @classmethod
    def _finite_priority(cls, value: float) -> float:
        return _finite(value, "priority")

    @field_validator("route")
    @classmethod
    def _route_sections_nonempty(cls, value: List[str]) -> List[str]:
        for section in value:
            if not section or not section.strip():
                raise ValueError("route entries must be non-empty section ids")
        return value


class DelayFeatures(BaseModel):
    """One block-window delay request (§16.3 exact features)."""

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    window_id: str
    section_id: str  # the section blocked by the window
    # §17.3 interval [e_w, l_w] — required for reporting and affinity context.
    earliest_start: datetime
    latest_end: datetime
    # §16.3 "time of day": minutes from midnight at the block start.
    time_of_day_minutes: float = Field(ge=0.0, le=1439.0)
    # §16.3 "historical delay patterns for the section": the caller's summary
    # statistic (e.g. mean historical delay in minutes for this section).
    historical_delay_minutes: float = Field(ge=0.0)
    # §16.3 "affected train IDs" (+ priority + route per train).
    affected_trains: List[AffectedTrain] = []
    # TRD §36 ``connected_to`` adjacency: section -> downstream sections.
    adjacency: Dict[str, List[str]] = {}

    @field_validator("window_id", "section_id")
    @classmethod
    def _ids_nonempty(cls, value: str, info) -> str:
        if not value or not value.strip():
            raise ValueError(f"{info.field_name} must be non-empty")
        return value

    @field_validator("time_of_day_minutes", "historical_delay_minutes")
    @classmethod
    def _finite_fields(cls, value: float, info) -> float:
        return _finite(value, info.field_name)

    @model_validator(mode="after")
    def _bounds_ordered(self) -> "DelayFeatures":
        if self.latest_end <= self.earliest_start:
            raise ValueError(
                f"window {self.window_id!r}: latest_end must be strictly "
                "after earliest_start"
            )
        return self

    @model_validator(mode="after")
    def _unique_train_ids(self) -> "DelayFeatures":
        seen = set()
        for train in self.affected_trains:
            if train.train_id in seen:
                raise ValueError(
                    f"duplicate train_id {train.train_id!r} — per-train delay "
                    "reporting requires unique identities"
                )
            seen.add(train.train_id)
        return self
