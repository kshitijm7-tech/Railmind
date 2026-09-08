from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class IngestionStatus(str, Enum):
    RECEIVED = "RECEIVED"
    VALIDATING = "VALIDATING"
    NORMALIZING = "NORMALIZING"
    PERSISTING = "PERSISTING"
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"

class RecordStatus(str, Enum):
    VALID = "VALID"
    VALID_WITH_WARNINGS = "VALID_WITH_WARNINGS"
    INVALID = "INVALID"
    QUARANTINED = "QUARANTINED"
    IMPORTED = "IMPORTED"
    DUPLICATE = "DUPLICATE"

class DataSourceType(str, Enum):
    TMS = "TMS"
    SMMS = "SMMS"
    TDMS = "TDMS"
    BDMS = "BDMS"
    COA = "COA"
    MANUAL = "MANUAL"
    FIXTURE = "FIXTURE"

class DataQualityResult(BaseModel):
    status: RecordStatus
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    checks_passed: int = 0
    checks_failed: int = 0

class IngestionRecord(BaseModel):
    record_id: str
    batch_id: str
    source: DataSourceType
    source_record_id: str
    received_at: datetime
    payload: Dict[str, Any]
    payload_hash: str
    status: RecordStatus
    quality_result: Optional[DataQualityResult] = None
    normalized_entity_type: Optional[str] = None
    normalized_entity_id: Optional[str] = None
    
class IngestionBatch(BaseModel):
    batch_id: str
    source: DataSourceType
    requested_at: datetime
    received_at: datetime
    completed_at: Optional[datetime] = None
    status: IngestionStatus
    schema_version: str
    adapter_version: str
    normalizer_version: str
    record_count: int = 0
    accepted_count: int = 0
    rejected_count: int = 0
    duplicate_count: int = 0
    correlation_id: str
    records: List[IngestionRecord] = Field(default_factory=list)

class QuarantineRecord(BaseModel):
    quarantine_id: str
    batch_id: str
    source: DataSourceType
    source_record_id: str
    raw_payload: Dict[str, Any]
    errors: List[str]
    warnings: List[str]
    created_at: datetime
    status: str = "UNRESOLVED"