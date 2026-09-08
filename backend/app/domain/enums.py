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
