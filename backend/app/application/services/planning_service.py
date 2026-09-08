from typing import List, Tuple
from app.domain.repositories import PlanRepository
from app.domain.models.planning import Plan

class PlanningService:
    def __init__(self, repository: PlanRepository):
        self._repository = repository

    def get_plans(self, page: int, page_size: int) -> Tuple[List[Plan], int]:
        return self._repository.get_all(page, page_size)
