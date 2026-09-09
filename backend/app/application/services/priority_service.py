from typing import List, Optional
from app.domain.engine.priority_engine import DeterministicPriorityEngine
from app.domain.engine.priority_models import PriorityResult
from app.domain.models.maintenance import MaintenanceTask, Defect
from app.domain.enums import DataState

_engine = DeterministicPriorityEngine()

class PriorityService:
    """
    Application-layer orchestration for P10 priority evaluation.
    Resolves maintenance tasks and linked defects, then delegates to
    the DeterministicPriorityEngine. Designed so a future ML engine
    can be swapped in without changes above this layer.
    """

    def evaluate_task(
        self,
        task: MaintenanceTask,
        defect: Optional[Defect] = None,
        num_train_impacts: int = 0,
        data_state: str = DataState.MOCKED.value,
    ) -> PriorityResult:
        return _engine.evaluate(
            task=task,
            defect=defect,
            num_train_impacts=num_train_impacts,
            data_state=data_state,
        )

    def evaluate_tasks(
        self,
        tasks: List[MaintenanceTask],
        defects_by_task: Optional[dict] = None,
        impacts_by_task: Optional[dict] = None,
        data_state: str = DataState.MOCKED.value,
    ) -> List[PriorityResult]:
        """Evaluate a batch of tasks and return results sorted by score descending."""
        defects_by_task = defects_by_task or {}
        impacts_by_task = impacts_by_task or {}

        results = [
            _engine.evaluate(
                task=t,
                defect=defects_by_task.get(t.task_id),
                num_train_impacts=impacts_by_task.get(t.task_id, 0),
                data_state=data_state,
            )
            for t in tasks
        ]
        return sorted(results, key=lambda r: r.score, reverse=True)