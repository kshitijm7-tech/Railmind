from typing import List, Optional
from datetime import datetime, timezone
from app.domain.models.maintenance import MaintenanceTask, PriorityBreakdown, Defect
from app.domain.models.common import DurationMinutes, Provenance
from app.domain.enums import Criticality, Department, TaskType, TaskStatus, DefectStatus, DefectSource, DefectSeverity, DataState, DataSource
from app.domain.repositories import MaintenanceRepository

class InMemoryMaintenanceRepository(MaintenanceRepository):
    def __init__(self):
        self._defects: List[Defect] = [
            Defect(
                defect_id="DEF-001",
                asset_id="AST-101",
                section_id="SEC-002",
                defect_type="SIGNAL_FAILURE",
                description="Signal showing red continuously",
                severity=DefectSeverity.CRITICAL,
                criticality=Criticality.CRITICAL,
                detected_at=datetime.now(timezone.utc),
                detected_by=DefectSource.DRIVER_REPORT,
                operational_impact="Stopping all traffic",
                is_safety_critical=True,
                urgency_hours=2,
                status=DefectStatus.LINKED,
                linked_task_id="TASK-001",
                department=Department.SIGNALING,
                provenance=Provenance(state=DataState.MOCKED, source=DataSource.MOCK_GENERATOR, generatedAt=datetime.now(timezone.utc))
            )
        ]

        self._tasks: List[MaintenanceTask] = [
            MaintenanceTask(
                task_id="TASK-001",
                asset_id="AST-101",
                section_id="SEC-002",
                type=TaskType.CORRECTIVE,
                status=TaskStatus.SCHEDULED,
                criticality=Criticality.CRITICAL,
                department=Department.SIGNALING,
                description="Fix faulty signal head - DEF-001",
                duration=DurationMinutes(expected=60, minimum=45, maximum=90),
                requires_power_block=True,
                requires_traffic_block=True,
                priority_breakdown=PriorityBreakdown(
                    safety_score=10,
                    reliability_score=8,
                    efficiency_score=5,
                    total_score=23
                )
            )
        ]

    def get_all_tasks(self, page: int, page_size: int) -> tuple[List[MaintenanceTask], int]:
        start = (page - 1) * page_size
        end = start + page_size
        return self._tasks[start:end], len(self._tasks)

    def get_task_by_id(self, task_id: str) -> Optional[MaintenanceTask]:
        return next((t for t in self._tasks if t.task_id == task_id), None)

    def get_all_defects(self, page: int, page_size: int) -> tuple[List[Defect], int]:
        start = (page - 1) * page_size
        end = start + page_size
        return self._defects[start:end], len(self._defects)

    def get_defect_by_id(self, defect_id: str) -> Optional[Defect]:
        return next((d for d in self._defects if d.defect_id == defect_id), None)
