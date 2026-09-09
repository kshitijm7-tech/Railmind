import os
import sys
from datetime import datetime, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import CorridorORM, TrackSectionORM, AssetORM, MaintenanceTaskORM, TrainORM, TrainPathORM

def seed():
    if not settings.DATABASE_ENABLED:
        print("Database not enabled. Seed aborted.")
        return
        
    db = SessionLocal()
    try:
        # Corridors
        c1 = db.query(CorridorORM).filter_by(corridor_id="CORR-01").first()
        if not c1:
            c1 = CorridorORM(corridor_id="CORR-01", name="Main Trunk", length_km=500.0, traffic_type="MIXED")
            db.add(c1)
            
        # Sections
        s1 = db.query(TrackSectionORM).filter_by(section_id="SEC-001").first()
        if not s1:
            s1 = TrackSectionORM(section_id="SEC-001", corridor_id="CORR-01", name="Alpha Segment", type="MAINLINE", length_m=10000, max_speed_kmh=120, status="OPERATIONAL")
            db.add(s1)
            
        s2 = db.query(TrackSectionORM).filter_by(section_id="SEC-002").first()
        if not s2:
            s2 = TrackSectionORM(section_id="SEC-002", corridor_id="CORR-01", name="Beta Segment", type="MAINLINE", length_m=15000, max_speed_kmh=100, status="OPERATIONAL")
            db.add(s2)
            
        db.commit()
        
        # Assets
        a1 = db.query(AssetORM).filter_by(asset_id="AST-101").first()
        if not a1:
            a1 = AssetORM(asset_id="AST-101", section_id="SEC-002", type="TRACK_CIRCUIT", condition="DEGRADED", last_maintained=datetime.now(timezone.utc))
            db.add(a1)
            
        db.commit()
        
        # Maintenance Task
        t1 = db.query(MaintenanceTaskORM).filter_by(task_id="TASK-001").first()
        if not t1:
            t1 = MaintenanceTaskORM(
                task_id="TASK-001", asset_id="AST-101", section_id="SEC-002",
                type="CORRECTIVE", status="PENDING", criticality="HIGH", department="SIGNAL",
                description="Fix circuit fault", duration_expected=120, duration_minimum=90, duration_maximum=150,
                requires_power_block=True, requires_traffic_block=True
            )
            db.add(t1)
            
        # Train
        trn = db.query(TrainORM).filter_by(train_id="TRN-500").first()
        if not trn:
            trn = TrainORM(
                train_id="TRN-500", name="Express 500", train_number="500X", type="PASSENGER",
                origin_station_id="STN-A", destination_station_id="STN-B",
                max_speed_kmh=120, length_m=300, weight_t=500, priority=1
            )
            db.add(trn)
            
        db.commit()
        print("Seed completed idempotently.")
    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()