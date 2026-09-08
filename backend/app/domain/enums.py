from enum import Enum

class Criticality(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class Department(str, Enum):
    TRACK = "TRACK"
    SIGNALING = "SIGNALING"
    POWER = "POWER"
    CIVIL = "CIVIL"

class TaskType(str, Enum):
    INSPECTION = "INSPECTION"
    REPAIR = "REPAIR"
    REPLACEMENT = "REPLACEMENT"

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class PlanStatus(str, Enum):
    DRAFT = "DRAFT"
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ACTIVE = "ACTIVE"

class PlanStrategy(str, Enum):
    NIGHT_ONLY = "NIGHT_ONLY"
    WEEKEND_CONTINUOUS = "WEEKEND_CONTINUOUS"
    MAX_THROUGHPUT = "MAX_THROUGHPUT"
    MIN_DISRUPTION = "MIN_DISRUPTION"

class DataState(str, Enum):
    MOCKED = "MOCKED"
    LIVE = "LIVE"

class DataSource(str, Enum):
    SYSTEM = "SYSTEM"
    USER = "USER"
    MOCK_GENERATOR = "MOCK_GENERATOR"
