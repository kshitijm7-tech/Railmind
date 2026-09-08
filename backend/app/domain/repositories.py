from typing import List, Optional, Protocol
from app.domain.models.maintenance import MaintenanceTask
from app.domain.models.planning import Plan

class MaintenanceTaskRepository(Protocol):
    def get_all(self, page: int, page_size: int) -> tuple[List[MaintenanceTask], int]:
        ...

    def get_by_id(self, task_id: str) -> Optional[MaintenanceTask]:
        ...

class PlanRepository(Protocol):
    def get_all(self, page: int, page_size: int) -> tuple[List[Plan], int]:
        ...

    def get_by_id(self, plan_id: str) -> Optional[Plan]:
        ...
