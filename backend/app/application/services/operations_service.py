from typing import List, Optional
from app.domain.models.operations import Train, TrainPath, OperationalWindow, TrainImpact
from app.domain.repositories import OperationsRepository

class OperationsService:
    def __init__(self, repo: OperationsRepository):
        self._repo = repo

    def get_trains(self, page: int, page_size: int) -> tuple[List[Train], int]:
        return self._repo.get_all_trains(page, page_size)

    def get_train(self, train_id: str) -> Optional[Train]:
        return self._repo.get_train_by_id(train_id)

    def get_train_paths(self, page: int, page_size: int) -> tuple[List[TrainPath], int]:
        return self._repo.get_all_train_paths(page, page_size)

    def get_operational_windows(self, page: int, page_size: int) -> tuple[List[OperationalWindow], int]:
        return self._repo.get_all_operational_windows(page, page_size)

    def get_train_impacts(self, page: int, page_size: int) -> tuple[List[TrainImpact], int]:
        return self._repo.get_all_train_impacts(page, page_size)
