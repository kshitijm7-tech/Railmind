from typing import List, Optional
from app.domain.models.infrastructure import RailwayAsset, TrackSection, Corridor
from app.domain.enums import AssetCategory, AssetOperationalStatus, SectionStatus, Criticality
from app.domain.repositories import InfrastructureRepository

class InMemoryInfrastructureRepository(InfrastructureRepository):
    def __init__(self):
        self._assets = [
            RailwayAsset(
                asset_id="AST-100",
                category=AssetCategory.TRACK,
                name="Main Track Switch A",
                location_section="SEC-001",
                criticality=Criticality.HIGH,
                is_operational=True
            ),
            RailwayAsset(
                asset_id="AST-101",
                category=AssetCategory.SIGNAL,
                name="Signal S-10",
                location_section="SEC-002",
                criticality=Criticality.CRITICAL,
                is_operational=False
            )
        ]

        self._sections = [
            TrackSection(
                section_id="SEC-001",
                name="North Corridor Section 1",
                start_station_id="ST-1",
                end_station_id="ST-2",
                length_km=15.5,
                max_speed_kmh=120,
                is_electrified=True,
                is_bidirectional=True,
                track_count=2
            ),
            TrackSection(
                section_id="SEC-002",
                name="North Corridor Section 2",
                start_station_id="ST-2",
                end_station_id="ST-3",
                length_km=20.0,
                max_speed_kmh=100,
                is_electrified=True,
                is_bidirectional=False,
                track_count=1
            )
        ]

        self._corridors = [
            Corridor(
                corridor_id="CORR-01",
                name="North Main Corridor",
                start_station_id="ST-1",
                end_station_id="ST-3",
                sections=["SEC-001", "SEC-002"]
            )
        ]

    def get_all_assets(self, page: int, page_size: int) -> tuple[List[RailwayAsset], int]:
        start = (page - 1) * page_size
        end = start + page_size
        return self._assets[start:end], len(self._assets)

    def get_asset_by_id(self, asset_id: str) -> Optional[RailwayAsset]:
        return next((a for a in self._assets if a.asset_id == asset_id), None)

    def get_all_track_sections(self, page: int, page_size: int) -> tuple[List[TrackSection], int]:
        start = (page - 1) * page_size
        end = start + page_size
        return self._sections[start:end], len(self._sections)

    def get_track_section_by_id(self, section_id: str) -> Optional[TrackSection]:
        return next((s for s in self._sections if s.section_id == section_id), None)

    def get_all_corridors(self, page: int, page_size: int) -> tuple[List[Corridor], int]:
        start = (page - 1) * page_size
        end = start + page_size
        return self._corridors[start:end], len(self._corridors)

    def get_corridor_by_id(self, corridor_id: str) -> Optional[Corridor]:
        return next((c for c in self._corridors if c.corridor_id == corridor_id), None)
