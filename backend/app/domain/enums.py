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
    Engineering = "Engineering"
    ST = "S&T"
    TRD = "TRD"
    OHE = "OHE"

class TaskType(str, Enum):
    INSPECTION = "INSPECTION"
    REPAIR = "REPAIR"
    REPLACEMENT = "REPLACEMENT"
    PREVENTIVE = "PREVENTIVE"
    CORRECTIVE = "CORRECTIVE"
    EMERGENCY = "EMERGENCY"

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class BlockStatus(str, Enum):
    DRAFT = "DRAFT"
    REQUESTED = "REQUESTED"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class PlanStatus(str, Enum):
    DRAFT = "DRAFT"
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    REJECTED = "REJECTED"

class PlanStrategy(str, Enum):
    MAINTENANCE_MAXIMIZED = "MAINTENANCE_MAXIMIZED"
    OPERATIONS_MAXIMIZED = "OPERATIONS_MAXIMIZED"
    BALANCED = "BALANCED"

class DataState(str, Enum):
    MOCKED = "MOCKED"
    LIVE = "LIVE"

class DataSource(str, Enum):
    SYSTEM = "SYSTEM"
    USER = "USER"
    MOCK_GENERATOR = "MOCK_GENERATOR"

# --- Infrastructure ---
class AssetCategory(str, Enum):
    TRACK = "TRACK"
    SIGNAL = "SIGNAL"
    OHE = "OHE"
    POINT = "POINT"
    BRIDGE = "BRIDGE"
    LEVEL_CROSSING = "LEVEL_CROSSING"

class AssetOperationalStatus(str, Enum):
    ACTIVE = "ACTIVE"
    MAINTENANCE = "MAINTENANCE"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"

class SectionStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    RESTRICTED = "RESTRICTED"

# --- Maintenance ---
class DefectSeverity(str, Enum):
    MINOR = "MINOR"
    MODERATE = "MODERATE"
    SEVERE = "SEVERE"
    CRITICAL = "CRITICAL"

class DefectStatus(str, Enum):
    DETECTED = "DETECTED"
    ASSESSED = "ASSESSED"
    LINKED = "LINKED"
    RECTIFIED = "RECTIFIED"
    DEFERRED = "DEFERRED"
    CLOSED = "CLOSED"

class DefectSource(str, Enum):
    INSPECTION = "INSPECTION"
    AUTOMATED_MONITORING = "AUTOMATED_MONITORING"
    DRIVER_REPORT = "DRIVER_REPORT"
    AEF_SCAN = "AEF_SCAN"
    BDMS_IMPORT = "BDMS_IMPORT"
    USER_REPORT = "USER_REPORT"

# --- Operations ---
class TrainType(str, Enum):
    EXPRESS = "EXPRESS"
    PASSENGER = "PASSENGER"
    FREIGHT = "FREIGHT"
    MAINTENANCE = "MAINTENANCE"

class TrainStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    DELAYED = "DELAYED"
    CANCELLED = "CANCELLED"

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ImpactType(str, Enum):
    DELAY = "DELAY"
    CANCELLATION = "CANCELLATION"
    REROUTING = "REROUTING"
    HOLD = "HOLD"
    PATH_CHANGE = "PATH_CHANGE"

class WindowAvailability(str, Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    MAINTENANCE = "MAINTENANCE"
    CLOSED = "CLOSED"

class DecisionStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DEFERRED = "DEFERRED"
    SUPERSEDED = "SUPERSEDED"

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    ENGINEER = "ENGINEER"
    PLANNER = "PLANNER"
    OPERATOR = "OPERATOR"
    SUPERVISOR = "SUPERVISOR"

