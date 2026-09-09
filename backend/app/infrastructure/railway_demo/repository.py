"""Operational repository seam over the synthetic railway-demo dataset.

Architecture::

    DemoSeedRepository
            ↓
    OperationalRepository interface
            ↑
            │
    Future: IndianRailwaysDataAdapter / ExternalFeedAdapter / ...

The existing canonical domain contracts (``app.domain.models.*``) are left
unchanged. The ``to_*`` adapters below translate the flat demo JSON rows
into those contracts; demo-only fields (headway, section_type, delays,
routes, planning windows) stay available in the raw rows for E09 / E05 /
P17 / P18, which consume this repository directly.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any, Dict, List, Optional, Protocol

from app.domain.enums import (
    AssetCategory,
    Criticality,
    Department,
    TaskStatus,
    TaskType,
    TrainType,
)
from app.domain.models.common import DurationMinutes, ScheduledTiming, TimeInterval
from app.domain.models.infrastructure import Corridor, RailwayAsset, TrackSection
from app.domain.models.maintenance import MaintenanceTask
from app.domain.models.operations import SectionTiming, Train, TrainService
from app.infrastructure.railway_demo.loader import DemoDataset, get_demo_dataset

TRAIN_TYPE_MAP = {
    "PREMIUM_EXPRESS": TrainType.EXPRESS,
    "SUPERFAST": TrainType.EXPRESS,
    "EXPRESS": TrainType.EXPRESS,
    "PASSENGER": TrainType.PASSENGER,
    "FREIGHT": TrainType.FREIGHT,
}

DEPARTMENT_MAP = {
    "TRACK": Department.TRACK,
    "ELECTRICAL": Department.OHE,
    "SIGNALLING": Department.SIGNALING,
    "SIGNALING": Department.SIGNALING,
}

ASSET_CATEGORY_MAP = {
    "TRACK": AssetCategory.TRACK,
    "OHE": AssetCategory.OHE,
    "SIGNALLING": AssetCategory.SIGNAL,
    "SIGNAL": AssetCategory.SIGNAL,
    "POINT": AssetCategory.POINT,
}

CRITICALITY_MAP = {
    "LOW": Criticality.LOW,
    "MEDIUM": Criticality.MEDIUM,
    "HIGH": Criticality.HIGH,
    "CRITICAL": Criticality.CRITICAL,
}

_MAX_SPEED_BY_TYPE = {
    TrainType.EXPRESS: 130,
    TrainType.PASSENGER: 110,
    TrainType.FREIGHT: 80,
}


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def priority_to_criticality(priority: int) -> Criticality:
    if priority >= 90:
        return Criticality.CRITICAL
    if priority >= 70:
        return Criticality.HIGH
    if priority >= 50:
        return Criticality.MEDIUM
    return Criticality.LOW


def to_track_section(raw: Dict[str, Any], stations_by_id: Dict[str, Dict[str, Any]]) -> TrackSection:
    from_code = stations_by_id.get(raw["from_station_id"], {}).get("code", raw["from_station_id"])
    to_code = stations_by_id.get(raw["to_station_id"], {}).get("code", raw["to_station_id"])
    section_type = raw.get("section_type")
    name = f"{from_code}–{to_code}"
    if section_type == "Freight_Bypass":
        name += " Freight Bypass"
    elif section_type == "Loop_Siding":
        name += " Loop Siding"
    elif section_type == "Goods_Loop":
        name += " Goods Loop"
    return TrackSection(
        section_id=raw["section_id"],
        name=name,
        start_station_id=raw["from_station_id"],
        end_station_id=raw["to_station_id"],
        length_km=float(raw["length_km"]),
        max_speed_kmh=int(raw["max_speed_kmph"]),
        is_electrified=bool(raw["electrified"]),
        is_bidirectional=int(raw.get("track_count", 1)) >= 2,
        track_count=int(raw.get("track_count", 1)),
    )


def to_corridor(corridor: Dict[str, Any], stations: List[Dict[str, Any]], sections: List[Dict[str, Any]]) -> Corridor:
    ordered = sorted(stations, key=lambda s: s["sequence"])
    return Corridor(
        corridor_id=corridor["corridor_id"],
        name=corridor["name"],
        start_station_id=ordered[0]["station_id"],
        end_station_id=ordered[-1]["station_id"],
        sections=[s["section_id"] for s in sections],
    )


def to_asset(raw: Dict[str, Any]) -> RailwayAsset:
    return RailwayAsset(
        asset_id=raw["asset_id"],
        category=ASSET_CATEGORY_MAP.get(raw["asset_type"], AssetCategory.TRACK),
        name=raw["asset_id"],
        location_section=raw["section_id"],
        criticality=CRITICALITY_MAP.get(raw["criticality"], Criticality.MEDIUM),
        is_operational=int(raw.get("health_score", 100)) >= 60,
    )


def to_train(raw: Dict[str, Any]) -> Train:
    train_type = TRAIN_TYPE_MAP.get(raw["train_type"], TrainType.EXPRESS)
    departure = _parse_dt(raw["scheduled_departure"])
    arrival = _parse_dt(raw["scheduled_arrival"])
    route = list(raw.get("route", []))
    total_seconds = max((arrival - departure).total_seconds(), 60.0)
    per_section = total_seconds / max(len(route), 1)
    timings: List[SectionTiming] = []
    for index, section_id in enumerate(route):
        entry = departure + timedelta(seconds=index * per_section)
        exit_ = departure + timedelta(seconds=(index + 1) * per_section)
        is_current = raw.get("current_section_id") == section_id and raw.get("current_status") == "RUNNING"
        delay = int(raw.get("current_delay_min", 0)) if is_current else 0
        timings.append(
            SectionTiming(
                section_id=section_id,
                entry_time=ScheduledTiming(scheduled=entry, delayMinutes=delay),
                exit_time=ScheduledTiming(scheduled=exit_, delayMinutes=delay),
            )
        )
    if train_type == TrainType.FREIGHT:
        length_m, weight_t = 700, 3000
    elif train_type == TrainType.PASSENGER:
        length_m, weight_t = 300, 800
    else:
        length_m, weight_t = 400, 1200
    return Train(
        service=TrainService(
            train_id=raw["train_id"],
            name=raw["name"],
            train_number=raw["train_number"],
            type=train_type,
            origin_station_id=raw["origin_station_id"],
            destination_station_id=raw["destination_station_id"],
            sections=timings,
        ),
        max_speed_kmh=_MAX_SPEED_BY_TYPE[train_type],
        length_m=length_m,
        weight_t=weight_t,
        priority=int(raw.get("priority", 3)),
    )


def to_task(raw: Dict[str, Any]) -> MaintenanceTask:
    title = raw.get("title", "")
    if "Inspection" in title:
        task_type = TaskType.INSPECTION
    elif "Preventive" in title:
        task_type = TaskType.PREVENTIVE
    else:
        task_type = TaskType.CORRECTIVE
    expected = int(raw["expected_duration_min"])
    department = DEPARTMENT_MAP.get(raw.get("department"), Department.TRACK)
    return MaintenanceTask(
        task_id=raw["task_id"],
        asset_id=raw["asset_id"],
        section_id=raw["section_id"],
        type=task_type,
        status=TaskStatus(raw.get("status", "PENDING")),
        criticality=priority_to_criticality(int(raw.get("priority", 50))),
        department=department,
        description=f"{title}. {raw.get('reason', '')}".strip(),
        requested_window=TimeInterval(
            start=_parse_dt(raw["earliest_start"]),
            end=_parse_dt(raw["latest_finish"]),
        ),
        duration=DurationMinutes(
            expected=expected,
            minimum=max(int(expected * 0.75), 1),
            maximum=int(expected * 1.25),
        ),
        requires_power_block=department == Department.OHE,
        requires_traffic_block=bool(raw.get("required_block", False)),
    )


class OperationalRepository(Protocol):
    """Future seam: any operational feed must provide these entities."""

    def get_corridor(self) -> Dict[str, Any]: ...
    def get_stations(self) -> List[Dict[str, Any]]: ...
    def get_sections(self) -> List[Dict[str, Any]]: ...
    def get_trains(self) -> List[Dict[str, Any]]: ...
    def get_train_movements(self) -> List[Dict[str, Any]]: ...
    def get_assets(self) -> List[Dict[str, Any]]: ...
    def get_maintenance_tasks(self) -> List[Dict[str, Any]]: ...
    def get_disruptions(self) -> List[Dict[str, Any]]: ...


class DemoSeedRepository(OperationalRepository):
    """OperationalRepository backed by the synthetic demo JSON files."""

    def __init__(self, dataset: DemoDataset | None = None):
        self._dataset = dataset or get_demo_dataset()

    def get_corridor(self) -> Dict[str, Any]:
        return self._dataset.corridor

    def get_stations(self) -> List[Dict[str, Any]]:
        return self._dataset.stations

    def get_sections(self) -> List[Dict[str, Any]]:
        return self._dataset.sections

    def get_trains(self) -> List[Dict[str, Any]]:
        return self._dataset.trains

    def get_train_movements(self) -> List[Dict[str, Any]]:
        return self._dataset.train_movements

    def get_assets(self) -> List[Dict[str, Any]]:
        return self._dataset.assets

    def get_maintenance_tasks(self) -> List[Dict[str, Any]]:
        return self._dataset.maintenance_tasks

    def get_disruptions(self) -> List[Dict[str, Any]]:
        return self._dataset.disruptions

    # -- Domain-adapted views (existing contracts) -------------------------
    def domain_track_sections(self) -> List[TrackSection]:
        stations_by_id = {s["station_id"]: s for s in self._dataset.stations}
        return [to_track_section(s, stations_by_id) for s in self._dataset.sections]

    def domain_corridors(self) -> List[Corridor]:
        return [to_corridor(self._dataset.corridor, self._dataset.stations, self._dataset.sections)]

    def domain_assets(self) -> List[RailwayAsset]:
        return [to_asset(a) for a in self._dataset.assets]

    def domain_trains(self) -> List[Train]:
        return [to_train(t) for t in self._dataset.trains]

    def domain_tasks(self) -> List[MaintenanceTask]:
        return [to_task(t) for t in self._dataset.maintenance_tasks]

    def get_station_by_id(self, station_id: str) -> Optional[Dict[str, Any]]:
        return next((s for s in self._dataset.stations if s["station_id"] == station_id), None)

    def get_section_by_id(self, section_id: str) -> Optional[Dict[str, Any]]:
        return next((s for s in self._dataset.sections if s["section_id"] == section_id), None)

    def get_train_by_id(self, train_id: str) -> Optional[Dict[str, Any]]:
        return next((t for t in self._dataset.trains if t["train_id"] == train_id), None)

    def get_disruption_by_id(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        return next((d for d in self._dataset.disruptions if d["scenario_id"] == scenario_id), None)


@lru_cache(maxsize=1)
def get_demo_seed_repository() -> DemoSeedRepository:
    return DemoSeedRepository()
