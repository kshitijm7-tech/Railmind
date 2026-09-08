"""Constraint evaluation context — the single input object every rule sees.

Assembled from engine input models plus explicit engine configuration
(constraint §20: no business constants hard-coded in rules). Pure data; the
engine never reads clocks, files or environment state.

Import graph: context → inputs, configuration (acyclic; inputs and
configuration never import context).
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from engine.models.inputs import (
    CandidateBlock,
    CorridorState,
    OperationalWindowRef,
    ResourceDemand,
    ResourcePool,
    ScheduledTaskRef,
    SectionOccupancy,
    SectionState,
    TaskRequirement,
    TimeInterval,
    TrainPathRef,
    require_timezone_aware,
)
from engine.constraints.configuration import ConstraintEngineConfig


class ConstraintContext(BaseModel):
    model_config = ConfigDict(frozen=True)

    candidate_block: CandidateBlock
    # Work the candidate claims to carry.
    tasks: List[TaskRequirement] = []
    # Task layout already fixed in the current plan (dependency references).
    scheduled_tasks: List[ScheduledTaskRef] = []
    train_paths: List[TrainPathRef] = []
    operational_windows: List[OperationalWindowRef] = []
    section_occupancies: List[SectionOccupancy] = []
    section_states: List[SectionState] = []
    corridors: List[CorridorState] = []
    resource_pools: List[ResourcePool] = []
    resource_demands: List[ResourceDemand] = []
    # Inclusive horizon bounds; None disables the horizon rule.
    planning_horizon: Optional[TimeInterval] = None
    configuration: ConstraintEngineConfig = ConstraintEngineConfig()

    @field_validator("planning_horizon")
    @classmethod
    def _tz_aware_horizon(cls, value: Optional[TimeInterval]) -> Optional[TimeInterval]:
        return value


def make_context(
    *,
    candidate_block: CandidateBlock,
    configuration: Optional[ConstraintEngineConfig] = None,
    **optional: object,
) -> ConstraintContext:
    """Convenience constructor for tests and future adapters."""
    data = {
        "candidate_block": candidate_block,
        "configuration": configuration or ConstraintEngineConfig(),
    }
    data.update(optional)
    return ConstraintContext(**data)


__all__ = ["ConstraintContext", "make_context", "require_timezone_aware"]
