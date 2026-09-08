from typing import List, Tuple, Optional
from app.domain.repositories import MaintenanceRepository
from app.domain.models.maintenance import MaintenanceTask, Defect

class MaintenanceService:
    def __init__(self, repository: MaintenanceRepository):
        self._repository = repository

    def get_tasks(self, page: int, page_size: int) -> Tuple[List[MaintenanceTask], int]:
        return self._repository.get_all_tasks(page, page_size)

    def get_task(self, task_id: str) -> Optional[MaintenanceTask]:
        return self._repository.get_task_by_id(task_id)

    def get_defects(self, page: int, page_size: int) -> Tuple[List[Defect], int]:
        return self._repository.get_all_defects(page, page_size)

    def get_defect(self, defect_id: str) -> Optional[Defect]:
        return self._repository.get_defect_by_id(defect_id)

    def get_defect_for_task(self, task_id: str) -> Optional[Defect]:
        """Return the first defect whose linked_task_id matches task_id."""
        all_defects, _ = self._repository.get_all_defects(1, 1000)
        return next((d for d in all_defects if d.linked_task_id == task_id), None)
