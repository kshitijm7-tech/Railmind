from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.infrastructure.database.base import Base
from datetime import datetime

class IngestionBatchORM(Base):
    __tablename__ = "ingestion_batches"
    
    batch_id: Mapped[str] = mapped_column(String, primary_key=True)
    source: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    schema_version: Mapped[str] = mapped_column(String, nullable=False)
    adapter_version: Mapped[str] = mapped_column(String, nullable=False)
    normalizer_version: Mapped[str] = mapped_column(String, nullable=False)
    record_count: Mapped[int] = mapped_column(Integer, default=0)
    accepted_count: Mapped[int] = mapped_column(Integer, default=0)
    rejected_count: Mapped[int] = mapped_column(Integer, default=0)
    duplicate_count: Mapped[int] = mapped_column(Integer, default=0)
    correlation_id: Mapped[str] = mapped_column(String, nullable=False)

class IngestionRecordORM(Base):
    __tablename__ = "ingestion_records"
    
    record_id: Mapped[str] = mapped_column(String, primary_key=True)
    batch_id: Mapped[str] = mapped_column(String, ForeignKey("ingestion_batches.batch_id"), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source_record_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    payload_hash: Mapped[str] = mapped_column(String, nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    normalized_entity_type: Mapped[str] = mapped_column(String, nullable=True)
    normalized_entity_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
    payload = mapped_column(JSONB, nullable=False)
    quality_result = mapped_column(JSONB, nullable=True)

class QuarantineRecordORM(Base):
    __tablename__ = "quarantine_records"
    
    quarantine_id: Mapped[str] = mapped_column(String, primary_key=True)
    batch_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source: Mapped[str] = mapped_column(String, nullable=False)
    source_record_id: Mapped[str] = mapped_column(String, nullable=False)
    raw_payload = mapped_column(JSONB, nullable=False)
    errors = mapped_column(JSONB, nullable=False)
    warnings = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)