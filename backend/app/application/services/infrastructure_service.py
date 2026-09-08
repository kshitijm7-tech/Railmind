from typing import List, Optional
from app.domain.models.infrastructure import RailwayAsset, TrackSection, Corridor
from app.domain.repositories import InfrastructureRepository

class InfrastructureService:
    def __init__(self, repo: InfrastructureRepository):
        self._repo = repo

    def get_assets(self, page: int, page_size: int) -> tuple[List[RailwayAsset], int]:
        return self._repo.get_all_assets(page, page_size)

    def get_asset(self, asset_id: str) -> Optional[RailwayAsset]:
        return self._repo.get_asset_by_id(asset_id)

    def get_track_sections(self, page: int, page_size: int) -> tuple[List[TrackSection], int]:
        return self._repo.get_all_track_sections(page, page_size)

    def get_track_section(self, section_id: str) -> Optional[TrackSection]:
        return self._repo.get_track_section_by_id(section_id)

    def get_corridors(self, page: int, page_size: int) -> tuple[List[Corridor], int]:
        return self._repo.get_all_corridors(page, page_size)

    def get_corridor(self, corridor_id: str) -> Optional[Corridor]:
        return self._repo.get_corridor_by_id(corridor_id)
