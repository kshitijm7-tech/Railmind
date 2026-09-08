from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry
from app.infrastructure.database.base import Base
from datetime import datetime

class CorridorORM(Base):
    __tablename__ = "corridors"
    
    corridor_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    length_km: Mapped[float] = mapped_column(Float, nullable=False)
    traffic_type: Mapped[str] = mapped_column(String, nullable=False)
    geometry = mapped_column(Geometry("LINESTRING", srid=4326), nullable=True)

    sections = relationship("TrackSectionORM", back_populates="corridor", cascade="all, delete-orphan")

class TrackSectionORM(Base):
    __tablename__ = "track_sections"
    
    section_id: Mapped[str] = mapped_column(String, primary_key=True)
    corridor_id: Mapped[str] = mapped_column(String, ForeignKey("corridors.corridor_id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    length_m: Mapped[int] = mapped_column(Integer, nullable=False)
    max_speed_kmh: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    geometry = mapped_column(Geometry("LINESTRING", srid=4326), nullable=True)

    corridor = relationship("CorridorORM", back_populates="sections")
    assets = relationship("AssetORM", back_populates="section", cascade="all, delete-orphan")
    maintenance_tasks = relationship("MaintenanceTaskORM", back_populates="section")

class AssetORM(Base):
    __tablename__ = "assets"
    
    asset_id: Mapped[str] = mapped_column(String, primary_key=True)
    section_id: Mapped[str] = mapped_column(String, ForeignKey("track_sections.section_id"), nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    condition: Mapped[str] = mapped_column(String, nullable=False)
    last_maintained: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    location = mapped_column(Geometry("POINT", srid=4326), nullable=True)

    section = relationship("TrackSectionORM", back_populates="assets")
    tasks = relationship("MaintenanceTaskORM", back_populates="asset", cascade="all, delete-orphan")

class MaintenanceTaskORM(Base):
    __tablename__ = "maintenance_tasks"
    
    task_id: Mapped[str] = mapped_column(String, primary_key=True)
    asset_id: Mapped[str] = mapped_column(String, ForeignKey("assets.asset_id"), nullable=False)
    section_id: Mapped[str] = mapped_column(String, ForeignKey("track_sections.section_id"), nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    criticality: Mapped[str] = mapped_column(String, nullable=False)
    department: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    duration_expected: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_minimum: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_maximum: Mapped[int] = mapped_column(Integer, nullable=False)
    
    requires_power_block: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_traffic_block: Mapped[bool] = mapped_column(Boolean, default=False)
    
    dependencies = mapped_column(JSONB, default=[])
    required_resources = mapped_column(JSONB, default=[])
    associated_defects = mapped_column(JSONB, default=[])
    
    asset = relationship("AssetORM", back_populates="tasks")
    section = relationship("TrackSectionORM", back_populates="maintenance_tasks")

class TrainORM(Base):
    __tablename__ = "trains"
    
    train_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    train_number: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    origin_station_id: Mapped[str] = mapped_column(String, nullable=False)
    destination_station_id: Mapped[str] = mapped_column(String, nullable=False)
    max_speed_kmh: Mapped[int] = mapped_column(Integer, nullable=False)
    length_m: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_t: Mapped[int] = mapped_column(Integer, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False)
    sections = mapped_column(JSONB, default=[])  # Storing section timings as JSONB for simplicity here

class TrainPathORM(Base):
    __tablename__ = "train_paths"
    
    train_id: Mapped[str] = mapped_column(String, ForeignKey("trains.train_id"), primary_key=True)
    segments = mapped_column(JSONB, default=[])  # Segment is section_id, start_time, end_time, conflicted
    constraints = mapped_column(JSONB, default=[])
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)

class PlanORM(Base):
    __tablename__ = "plans"
    
    plan_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    strategy: Mapped[str] = mapped_column(String, nullable=False)
    metrics = mapped_column(JSONB, nullable=False)
    version = mapped_column(JSONB, nullable=False)
    provenance = mapped_column(JSONB, nullable=False)

    blocks = relationship("BlockORM", back_populates="plan", cascade="all, delete-orphan")

class BlockORM(Base):
    __tablename__ = "blocks"
    
    block_id: Mapped[str] = mapped_column(String, primary_key=True)
    plan_id: Mapped[str] = mapped_column(String, ForeignKey("plans.plan_id"), nullable=False)
    section_id: Mapped[str] = mapped_column(String, nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    required_power_off: Mapped[bool] = mapped_column(Boolean, default=False)
    is_integrated: Mapped[bool] = mapped_column(Boolean, default=False)
    tasks = mapped_column(JSONB, default=[])

    plan = relationship("PlanORM", back_populates="blocks")

class SimulationRunORM(Base):
    __tablename__ = "simulation_runs"
    
    simulation_run_id: Mapped[str] = mapped_column(String, primary_key=True)
    scenario_id: Mapped[str] = mapped_column(String, nullable=False)
    plan_id: Mapped[str] = mapped_column(String, nullable=False)
    plan_version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    engine_version: Mapped[str] = mapped_column(String, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    configuration = mapped_column(JSONB, default={})
    provenance = mapped_column(JSONB, nullable=False)
    result = mapped_column(JSONB, nullable=True)  # Store complete results + events

class DecisionORM(Base):
    __tablename__ = "decisions"
    
    decision_id: Mapped[str] = mapped_column(String, primary_key=True)
    plan_id: Mapped[str] = mapped_column(String, nullable=False)
    plan_version: Mapped[int] = mapped_column(Integer, nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    justification: Mapped[str] = mapped_column(Text, nullable=False)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    decided_by: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    decision_metadata = mapped_column(JSONB, default={})
class ForecastResultORM(Base):
    __tablename__ = "forecast_results"
    
    forecast_id: Mapped[str] = mapped_column(String, primary_key=True)
    request_id: Mapped[str] = mapped_column(String, nullable=False)
    target_type: Mapped[str] = mapped_column(String, nullable=False)
    scope: Mapped[str] = mapped_column(String, nullable=False)
    scope_id: Mapped[str] = mapped_column(String, nullable=True)
    model_name: Mapped[str] = mapped_column(String, nullable=False)
    model_version: Mapped[str] = mapped_column(String, nullable=False)
    quality_score: Mapped[float] = mapped_column(Float, nullable=False)
    quality_level: Mapped[str] = mapped_column(String, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    predictions = mapped_column(JSONB, nullable=False)
    provenance = mapped_column(JSONB, nullable=False)