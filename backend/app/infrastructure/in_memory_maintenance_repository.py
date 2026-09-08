from typing import List, Optional
from app.domain.models.maintenance import MaintenanceTask, PriorityBreakdown
from app.domain.models.common import DurationMinutes
from app.domain.enums import Criticality, Department, TaskType, TaskStatus

class InMemoryMaintenanceTaskRepository:
    def __init__(self):
        self._tasks: List[MaintenanceTask] = [
            MaintenanceTask(
                task_id="TASK-001",
                asset_id="ASSET-TRACK-101",
                section_id="SEC-A",
                type=TaskType.INSPECTION,
                status=TaskStatus.SCHEDULED,
                criticality=Criticality.HIGH,
                department=Department.TRACK,
                description="Track inspection due to reported anomaly",
                duration=DurationMinutes(value=120),
                requires_power_block=False,
                requires_traffic_block=True,
                priority_breakdown=PriorityBreakdown(
                    safetyScore=9,
                    operationalImpact=5,
                    maintenanceBacklog=2,
                    resourceAvailability=8
                )
            ),
            MaintenanceTask(
                task_id="TASK-002",
                asset_id="ASSET-SIG-202",
                section_id="SEC-B",
                type=TaskType.REPAIR,
                status=TaskStatus.PENDING,
                criticality=Criticality.CRITICAL,
                department=Department.SIGNALING,
                description="Fix faulty signal head",
                duration=DurationMinutes(value=60),
                requires_power_block=True,
                requires_traffic_block=True
            ),
            MaintenanceTask(
                task_id="TASK-003",
                asset_id="ASSET-PWR-303",
                section_id="SEC-C",
                type=TaskType.REPLACEMENT,
                status=TaskStatus.COMPLETED,
                criticality=Criticality.MEDIUM,
                department=Department.POWER,
                description="Routine catenary wire replacement",
                duration=DurationMinutes(value=240),
                requires_power_block=True,
                requires_traffic_block=True
            )
        ]

    def get_all(self, page: int, page_size: int) -> tuple[List[MaintenanceTask], int]:
        start = (page - 1) * page_size
        end = start + page_size
        return self._tasks[start:end], len(self._tasks)

    def get_by_id(self, task_id: str) -> Optional[MaintenanceTask]:
        for t in self._tasks:
            if t.task_id == task_id:
                return t
        return None
