from typing import List, Optional
from pydantic import BaseModel
from app.domain.enums import AssetCategory, AssetOperationalStatus, SectionStatus, Criticality

class RailwayAsset(BaseModel):
    asset_id: str
    category: AssetCategory
    name: str
    location_section: Optional[str] = None
    location_station: Optional[str] = None
    criticality: Criticality
    is_operational: bool

class TrackSection(BaseModel):
    section_id: str
    name: str
    start_station_id: str
    end_station_id: str
    length_km: float
    max_speed_kmh: int
    is_electrified: bool
    is_bidirectional: bool
    track_count: int

class Station(BaseModel):
    station_id: str
    name: str
    code: str
    latitude: float
    longitude: float
    platform_count: int

class Corridor(BaseModel):
    corridor_id: str
    name: str
    start_station_id: str
    end_station_id: str
    sections: List[str]

class RailwayNetwork(BaseModel):
    stations: List[Station]
    sections: List[TrackSection]
    corridors: List[Corridor]
    assets: List[RailwayAsset]
