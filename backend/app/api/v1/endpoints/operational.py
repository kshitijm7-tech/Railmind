"""Canonical operational read APIs over the synthetic railway-demo dataset.

Covers the entities that have no dedicated domain endpoint yet
(stations, train movements, disruptions) plus a canonical ``/sections``
alias for ``/track-sections``. All data comes from the DemoSeedRepository —
no hardcoded operational copies.

SYNTHETIC DATA: responses are demonstration scenario data, not live
Indian Railways operations.
"""

from datetime import datetime, timezone
from typing import List, Optional
import math
import uuid

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.api.models import ApiListResponse, ApiMeta, ApiResponse, PaginationMeta
from app.infrastructure.railway_demo.repository import get_demo_seed_repository

router = APIRouter()


def get_meta() -> ApiMeta:
    return ApiMeta(
        timestamp=datetime.now(timezone.utc).isoformat(),
        requestId=str(uuid.uuid4()),
        version="v1.0.0",
    )


def _paginate(items: list, page: int, page_size: int):
    total = len(items)
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    start = (page - 1) * page_size
    return items[start:start + page_size], total, total_pages


class StationView(BaseModel):
    station_id: str
    code: str
    name: str
    sequence: int
    km: float
    category: str
    platforms: int
    loop_lines: int
    is_junction: bool


class SectionView(BaseModel):
    section_id: str
    from_station_id: str
    to_station_id: str
    length_km: float
    track_count: int
    electrified: bool
    max_speed_kmph: int
    headway_min: int
    section_type: Optional[str] = "Main_Line"


class TrainMovementView(BaseModel):
    movement_id: str
    train_id: str
    section_id: str
    entry_time: str
    exit_time: str
    status: str
    delay_minutes: int


class DisruptionView(BaseModel):
    scenario_id: str
    type: str
    section_id: str
    related_task_id: Optional[str] = None
    planned_start: Optional[str] = None
    planned_end: Optional[str] = None
    actual_end: Optional[str] = None
    severity: str
    description: str


@router.get("/stations", response_model=ApiListResponse[StationView])
def get_stations(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    is_junction: Optional[bool] = Query(None),
):
    repo = get_demo_seed_repository()
    items = repo.get_stations()
    if is_junction is not None:
        items = [s for s in items if bool(s.get("is_junction")) == is_junction]
    page_items, total, total_pages = _paginate(items, page, page_size)
    return ApiListResponse(
        data=[StationView(**s) for s in page_items],
        pagination=PaginationMeta(
            totalItems=total, page=page, pageSize=page_size, totalPages=total_pages
        ),
        meta=get_meta(),
    )


@router.get("/stations/{station_id}", response_model=ApiResponse[StationView])
def get_station(station_id: str):
    repo = get_demo_seed_repository()
    item = repo.get_station_by_id(station_id)
    if not item:
        raise HTTPException(status_code=404, detail="Station not found")
    return ApiResponse(data=StationView(**item), meta=get_meta())


@router.get("/sections", response_model=ApiListResponse[SectionView])
def get_sections(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    corridor_id: Optional[str] = Query(None),
    section_type: Optional[str] = Query(None),
):
    repo = get_demo_seed_repository()
    items = repo.get_sections()
    if corridor_id is not None and corridor_id != repo.get_corridor()["corridor_id"]:
        items = []
    if section_type is not None:
        items = [s for s in items if s.get("section_type", "Main_Line") == section_type]
    page_items, total, total_pages = _paginate(items, page, page_size)
    return ApiListResponse(
        data=[SectionView(**s) for s in page_items],
        pagination=PaginationMeta(
            totalItems=total, page=page, pageSize=page_size, totalPages=total_pages
        ),
        meta=get_meta(),
    )


@router.get("/sections/{section_id}", response_model=ApiResponse[SectionView])
def get_section(section_id: str):
    repo = get_demo_seed_repository()
    item = repo.get_section_by_id(section_id)
    if not item:
        raise HTTPException(status_code=404, detail="Section not found")
    return ApiResponse(data=SectionView(**item), meta=get_meta())


@router.get("/train-movements", response_model=ApiListResponse[TrainMovementView])
def get_train_movements(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    train_id: Optional[str] = Query(None),
    section_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    repo = get_demo_seed_repository()
    items = repo.get_train_movements()
    if train_id is not None:
        items = [m for m in items if m["train_id"] == train_id]
    if section_id is not None:
        items = [m for m in items if m["section_id"] == section_id]
    if status is not None:
        items = [m for m in items if m["status"] == status]
    page_items, total, total_pages = _paginate(items, page, page_size)
    return ApiListResponse(
        data=[TrainMovementView(**m) for m in page_items],
        pagination=PaginationMeta(
            totalItems=total, page=page, pageSize=page_size, totalPages=total_pages
        ),
        meta=get_meta(),
    )


@router.get("/disruptions", response_model=ApiListResponse[DisruptionView])
def get_disruptions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    section_id: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    type: Optional[str] = Query(None, alias="type"),
):
    repo = get_demo_seed_repository()
    items = repo.get_disruptions()
    if section_id is not None:
        items = [d for d in items if d["section_id"] == section_id]
    if severity is not None:
        items = [d for d in items if d["severity"] == severity]
    if type is not None:
        items = [d for d in items if d["type"] == type]
    page_items, total, total_pages = _paginate(items, page, page_size)
    return ApiListResponse(
        data=[DisruptionView(**d) for d in page_items],
        pagination=PaginationMeta(
            totalItems=total, page=page, pageSize=page_size, totalPages=total_pages
        ),
        meta=get_meta(),
    )


@router.get("/disruptions/{scenario_id}", response_model=ApiResponse[DisruptionView])
def get_disruption(scenario_id: str):
    repo = get_demo_seed_repository()
    item = repo.get_disruption_by_id(scenario_id)
    if not item:
        raise HTTPException(status_code=404, detail="Disruption scenario not found")
    return ApiResponse(data=DisruptionView(**item), meta=get_meta())


@router.get("/corridor", response_model=ApiResponse[dict])
def get_corridor():
    """Canonical corridor C-07 metadata (raw demo shape)."""
    repo = get_demo_seed_repository()
    return ApiResponse(data=repo.get_corridor(), meta=get_meta())
