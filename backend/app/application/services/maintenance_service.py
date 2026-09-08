from typing import List, Tuple
from app.domain.repositories import MaintenanceTaskRepository
from app.domain.models.maintenance import MaintenanceTask

class MaintenanceService:
    def __init__(self, repository: MaintenanceTaskRepository):
        self._repository = repository

    def get_tasks(self, page: int, page_size: int) -> Tuple[List[MaintenanceTask], int]:
        return self._repository.get_all(page, page_size)
