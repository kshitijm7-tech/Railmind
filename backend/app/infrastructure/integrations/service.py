import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.infrastructure.integrations.models import (
    DataSourceType, IngestionBatch, IngestionRecord, QuarantineRecord, 
    IngestionStatus, RecordStatus
)
from app.infrastructure.integrations.validators.quality_engine import DataQualityEngine
from app.infrastructure.integrations.normalizers.registry import NormalizerRegistry

# Import adapter mocks
from app.infrastructure.integrations.adapters.mocks import (
    MockTMSAdapter, MockSMMSAdapter, MockTDMSAdapter, MockBDMSAdapter, MockCOAAdapter
)

class IngestionService:
    def __init__(self):
        self.quality_engine = DataQualityEngine()
        self.normalizer = NormalizerRegistry()
        self.adapters = {
            DataSourceType.TMS: MockTMSAdapter(),
            DataSourceType.SMMS: MockSMMSAdapter(),
            DataSourceType.TDMS: MockTDMSAdapter(),
            DataSourceType.BDMS: MockBDMSAdapter(),
            DataSourceType.COA: MockCOAAdapter(),
        }
        # In memory simulation of DB persistence for non-PostgreSQL runs
        self._batches = {}
        self._records = {}
        self._quarantines = {}

    def run_ingestion(self, source_type: DataSourceType, correlation_id: str) -> IngestionBatch:
        adapter = self.adapters.get(source_type)
        if not adapter:
            raise ValueError(f"No adapter found for {source_type}")
            
        received_at = datetime.now(timezone.utc)
        batch = IngestionBatch(
            batch_id=f"BATCH-{uuid.uuid4().hex[:8]}",
            source=source_type,
            requested_at=received_at,
            received_at=received_at,
            status=IngestionStatus.RECEIVED,
            schema_version="1.0",
            adapter_version=adapter.adapter_version,
            normalizer_version="1.0",
            correlation_id=correlation_id
        )
        
        # 1. Fetch Raw Data
        raw_payloads = adapter.fetch({})
        
        batch.status = IngestionStatus.VALIDATING
        
        for payload in raw_payloads:
            batch.record_count += 1
            
            # Hash payload
            payload_str = json.dumps(payload, sort_keys=True)
            payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()
            
            # Identify source record id loosely for mocks
            source_rec_id = payload.get("tms_id") or payload.get("smms_task_id") or payload.get("tdms_asset_id") or f"GEN-{uuid.uuid4().hex[:6]}"
            
            # Idempotency check (simplified)
            idem_key = f"{source_type.value}_{source_rec_id}"
            if idem_key in self._records:
                batch.duplicate_count += 1
                continue
            
            # Validate
            quality_result = self.quality_engine.validate(source_type.value, payload)
            
            rec = IngestionRecord(
                record_id=f"REC-{uuid.uuid4().hex[:8]}",
                batch_id=batch.batch_id,
                source=source_type,
                source_record_id=source_rec_id,
                received_at=datetime.now(timezone.utc),
                payload=payload,
                payload_hash=payload_hash,
                status=quality_result.status,
                quality_result=quality_result
            )
            
            if quality_result.status in [RecordStatus.INVALID, RecordStatus.QUARANTINED]:
                batch.rejected_count += 1
                quarantine = QuarantineRecord(
                    quarantine_id=f"QRN-{uuid.uuid4().hex[:8]}",
                    batch_id=batch.batch_id,
                    source=source_type,
                    source_record_id=source_rec_id,
                    raw_payload=payload,
                    errors=quality_result.errors,
                    warnings=quality_result.warnings,
                    created_at=datetime.now(timezone.utc)
                )
                self._quarantines[quarantine.quarantine_id] = quarantine
            else:
                # Normalize
                domain_entity = self.normalizer.normalize(source_type, payload)
                if domain_entity:
                    rec.normalized_entity_type = domain_entity.__class__.__name__
                    
                    if hasattr(domain_entity, "service") and hasattr(domain_entity.service, "train_id"):
                        rec.normalized_entity_id = domain_entity.service.train_id
                    else:
                        rec.normalized_entity_id = getattr(domain_entity, "task_id", getattr(domain_entity, "asset_id", None))
                    
                batch.accepted_count += 1
                
            self._records[idem_key] = rec
            batch.records.append(rec)
            
        batch.status = IngestionStatus.COMPLETED
        batch.completed_at = datetime.now(timezone.utc)
        self._batches[batch.batch_id] = batch
        
        return batch