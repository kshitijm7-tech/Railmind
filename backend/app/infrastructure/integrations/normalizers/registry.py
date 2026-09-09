from typing import Dict, Any, Optional
from datetime import datetime
from app.infrastructure.integrations.models import DataSourceType
from app.domain.models.operations import Train, TrainPath, PathSegment, SectionTiming
from app.domain.models.maintenance import MaintenanceTask
from app.domain.models.infrastructure import RailwayAsset, TrackSection
from app.domain.models.common import TimeInterval

class NormalizerRegistry:
    def normalize(self, source_type: DataSourceType, payload: Dict[str, Any]) -> Any:
        if source_type == DataSourceType.TMS:
            return self._normalize_tms(payload)
        elif source_type == DataSourceType.SMMS:
            return self._normalize_smms(payload)
        elif source_type == DataSourceType.TDMS:
            return self._normalize_tdms(payload)
        return None

    def _normalize_tms(self, payload: Dict[str, Any]) -> Train:
        from app.domain.models.operations import TrainService
        return Train(
            service=TrainService(
                train_id=payload.get("tms_id"),
                name=payload.get("name"),
                train_number=payload.get("number"),
                type=payload.get("train_type"),
                origin_station_id=payload.get("origin"),
                destination_station_id=payload.get("destination"),
                sections=[]
            ),
            max_speed_kmh=payload.get("max_velocity_kmh"),
            length_m=payload.get("length_meters"),
            weight_t=payload.get("weight_tons"),
            priority=payload.get("priority_class")
        )

    def _normalize_smms(self, payload: Dict[str, Any]) -> MaintenanceTask:
        return MaintenanceTask(
            task_id=payload.get("smms_task_id"),
            asset_id=payload.get("asset_reference"),
            section_id=payload.get("section_reference"),
            type=payload.get("maintenance_type"),
            status=payload.get("status"),
            criticality=payload.get("criticality_level"),
            department=payload.get("department"),
            description=payload.get("desc"),
            duration_expected=payload.get("duration_mins"),
            duration_minimum=payload.get("min_mins"),
            duration_maximum=payload.get("max_mins"),
            requires_power_block=payload.get("power_block", False),
            requires_traffic_block=payload.get("traffic_block", False)
        )

    def _normalize_tdms(self, payload: Dict[str, Any]) -> RailwayAsset:
        return RailwayAsset(
            asset_id=payload.get("tdms_asset_id"),
            section_id=payload.get("section"),
            type=payload.get("asset_type"),
            condition=payload.get("current_condition"),
            last_maintained=None # Simplification
        )