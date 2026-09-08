"""Hard constraint rules (PRD §27, blueprint §17.4, TRD §24)."""

from engine.constraints.hard.duration import BlockDurationRule
from engine.constraints.hard.operational_window import OperationalWindowRule
from engine.constraints.hard.train_conflict import TrainConflictRule
from engine.constraints.hard.track_occupancy import TrackOccupancyRule
from engine.constraints.hard.resource_exclusivity import ResourceExclusivityRule
from engine.constraints.hard.corridor_availability import CorridorAvailabilityRule
from engine.constraints.hard.planning_horizon import PlanningHorizonRule
from engine.constraints.hard.task_deadline import TaskDeadlineRule
from engine.constraints.hard.task_dependency import TaskDependencyRule

__all__ = [
    "BlockDurationRule",
    "OperationalWindowRule",
    "TrainConflictRule",
    "TrackOccupancyRule",
    "ResourceExclusivityRule",
    "CorridorAvailabilityRule",
    "PlanningHorizonRule",
    "TaskDeadlineRule",
    "TaskDependencyRule",
]
