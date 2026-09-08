"""Engine input models for the Constraint Engine (E01).

These models are the canonical engine-facing vocabulary. They deliberately
mirror the shared contracts in ``frontend/contracts/`` (TimeInterval,
DurationMinutes, Block, TrainPath, OperationalWindow, Corridor) so that a
backend adapter can map contract/backend data onto them 1:1, while the engine
itself stays independent from FastAPI, SQLAlchemy and the frontend.

Mapping notes (contract → engine input):
- ``contracts/common/time.ts``        → TimeInterval, DurationEstimate
- ``contracts/planning/block.ts``     → CandidateBlock
- ``contracts/operations/train-path.ts`` → TrainPathRef / PathSegmentRef
- ``contracts/operations/operational-window.ts`` → OperationalWindowRef
- ``contracts/infrastructure/corridor.ts`` → CorridorState
- ``contracts/maintenance/maintenance-task.ts`` → TaskRequirement

Where the canonical contracts do not yet define a field the documented
constraints require (e.g. section availability status, task deadline), the
smallest clean engine-level abstraction is provided here and the gap is
recorded in docs/E01_Report.md.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator


def require_timezone_aware(value: datetime, field_name: str) -> datetime:
    """Reject naive datetimes so all interval comparisons are unambiguous."""
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        raise ValueError(
            f"{field_name} must be timezone-aware (ISO-8601 with offset); got naive datetime {value!r}"
        )
    return value


class WindowAvailability(str, Enum):
    """Mirrors ``contracts/operations/operational-window.ts``."""

    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    MAINTENANCE = "MAINTENANCE"
    CLOSED = "CLOSED"


class SectionStatus(str, Enum):
    """Mirrors the backend ``SectionStatus`` enum (infrastructure availability)."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"
    RESTRICTED = "RESTRICTED"


class TimeInterval(BaseModel):
    """Half-open-in-spirit interval; containment is inclusive, overlap is strict.

    Mirrors ``contracts/common/time.ts::TimeInterval``. The model intentionally
    does NOT reject ``end <= start``: an invalid duration is a domain outcome
    (rule FAIL with evidence), not a construction error.
    """

    model_config = ConfigDict(frozen=True)

    start: datetime
    end: datetime

    @field_validator("start", "end")
    @classmethod
    def _tz_aware(cls, value: datetime) -> datetime:
        return require_timezone_aware(value, cls.__name__)

    @property
    def minutes(self) -> float:
        return (self.end - self.start).total_seconds() / 60.0

    def contains(self, other: "TimeInterval") -> bool:
        """Inclusive containment (boundary instants count as contained)."""
        return self.start <= other.start and other.end <= self.end

    def overlaps(self, other: "TimeInterval") -> bool:
        """Strict overlap: adjacent intervals (touching endpoints) do NOT overlap."""
        return self.start < other.end and other.start < self.end

    def overlap_minutes(self, other: "TimeInterval") -> float:
        if not self.overlaps(other):
            return 0.0
        return (min(self.end, other.end) - max(self.start, other.start)).total_seconds() / 60.0


class DurationEstimate(BaseModel):
    """Mirrors ``contracts/common/time.ts::DurationMinutes`` (expected/minimum/maximum)."""

    model_config = ConfigDict(frozen=True)

    expected: int
    minimum: int
    maximum: int


class CandidateBlock(BaseModel):
    """The proposed block under evaluation (mirrors ``contracts/planning/block.ts``)."""

    model_config = ConfigDict(frozen=True)

    block_id: Optional[str] = None
    section_id: str
    interval: TimeInterval
    task_ids: List[str] = []
    # Pools the candidate explicitly claims (e.g. exclusive machinery). Crew
    # demand is derived from task departments instead.
    resource_pool_ids: List[str] = []


class TaskRequirement(BaseModel):
    """Maintenance work that a candidate block may carry.

    Fields follow the canonical task contracts plus the blueprint §11.2 fields
    the documented hard constraints need (deadline, dependencies).
    """

    model_config = ConfigDict(frozen=True)

    task_id: str
    section_id: str
    department: str
    duration: DurationEstimate
    crew_units_required: int = 0
    # Blueprint §11.2 ``latest_finish`` (may be null).
    latest_finish: Optional[datetime] = None
    # Blueprint §11.2 ``dependency_task_ids``.
    depends_on: List[str] = []

    @field_validator("latest_finish")
    @classmethod
    def _tz_aware_deadline(cls, value: Optional[datetime]) -> Optional[datetime]:
        if value is None:
            return None
        return require_timezone_aware(value, "latest_finish")


class PathSegmentRef(BaseModel):
    """Mirrors ``contracts/operations/train-path.ts::PathSegment`` (subset)."""

    model_config = ConfigDict(frozen=True)

    section_id: str
    interval: TimeInterval


class TrainPathRef(BaseModel):
    """Mirrors ``contracts/operations/train-path.ts::TrainPath`` (subset)."""

    model_config = ConfigDict(frozen=True)

    train_id: str
    segments: List[PathSegmentRef] = []


class OperationalWindowRef(BaseModel):
    """Mirrors ``contracts/operations/operational-window.ts::OperationalWindow``."""

    model_config = ConfigDict(frozen=True)

    window_id: str
    section_id: str
    interval: TimeInterval
    availability: WindowAvailability


class SectionOccupancy(BaseModel):
    """An existing activity already occupying a section (block, work, closure)."""

    model_config = ConfigDict(frozen=True)

    occupancy_id: str
    section_id: str
    interval: TimeInterval
    kind: str = "MAINTENANCE"


class ScheduledTaskRef(BaseModel):
    """Where a task is already scheduled in the current plan (for precedence)."""

    model_config = ConfigDict(frozen=True)

    task_id: str
    block_id: Optional[str] = None
    interval: TimeInterval


class ResourcePool(BaseModel):
    """A crew pool or equipment pool.

    Department semantics follow blueprint §11.5 (crew pools per department);
    ``availability`` is the pool's shift window when known (may be None).
    """

    model_config = ConfigDict(frozen=True)

    pool_id: str
    department: str
    units_available: int
    availability: Optional[TimeInterval] = None
    is_exclusive: bool = False


class ResourceDemand(BaseModel):
    """An existing allocation against a resource pool."""

    model_config = ConfigDict(frozen=True)

    demand_id: str
    pool_id: str
    units: int
    interval: TimeInterval


class SectionState(BaseModel):
    """Infrastructure availability for a section (engine-level abstraction)."""

    model_config = ConfigDict(frozen=True)

    section_id: str
    status: SectionStatus


class CorridorState(BaseModel):
    """Corridor membership and availability (engine-level abstraction).

    The canonical ``contracts/infrastructure/corridor.ts::Corridor`` defines
    membership (``sections``) but no availability flag; ``is_available`` is the
    smallest engine-side extension that the documented corridor-availability
    constraint needs. Recorded as a contract gap in docs/E01_Report.md.
    """

    model_config = ConfigDict(frozen=True)

    corridor_id: str
    section_ids: List[str] = []
    is_available: bool = True
