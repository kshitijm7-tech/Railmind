from typing import List, Optional
from datetime import datetime, timezone, timedelta
from app.domain.models.operations import Train, TrainPath, OperationalWindow, TrainImpact, TrainService, SectionTiming, PathSegment, PathConstraint
from app.domain.models.common import ScheduledTiming, TimeInterval
from app.domain.enums import TrainType, TrainStatus, RiskLevel, ImpactType, WindowAvailability
from app.domain.repositories import OperationsRepository

class InMemoryOperationsRepository(OperationsRepository):
    def __init__(self):
        try:
            from app.infrastructure.railway_demo.repository import DemoSeedRepository

            seed = DemoSeedRepository()
            self._trains = seed.domain_trains()
        except Exception:
            self._trains = []
        if not getattr(self, "_trains", []):
            now = datetime.now(timezone.utc)
            self._trains = [
                Train(
                    service=TrainService(
                        train_id="TRN-500",
                        name="Rajdhani Express",
                        train_number="12951",
                        type=TrainType.EXPRESS,
                        origin_station_id="ST-1",
                        destination_station_id="ST-3",
                        sections=[
                            SectionTiming(
                                section_id="SEC-001",
                                entry_time=ScheduledTiming(scheduled=now, delayMinutes=0),
                                exit_time=ScheduledTiming(scheduled=now + timedelta(minutes=15), delayMinutes=0)
                            ),
                            SectionTiming(
                                section_id="SEC-002",
                                entry_time=ScheduledTiming(scheduled=now + timedelta(minutes=15), delayMinutes=0),
                                exit_time=ScheduledTiming(scheduled=now + timedelta(minutes=35), delayMinutes=0)
                            )
                        ]
                    ),
                    max_speed_kmh=130,
                    length_m=400,
                    weight_t=1200,
                    priority=1
                )
            ]
        else:
            now = datetime.now(timezone.utc)
        
        self._paths = [
            TrainPath(
                train_id="TRN-500",
                segments=[
                    PathSegment(
                        section_id="SEC-001",
                        interval=TimeInterval(start=now, end=now + timedelta(minutes=15)),
                        is_conflicted=False
                    )
                ],
                constraints=[
                    PathConstraint(type="SPEED_RESTRICTION", description="Max 100 kmph")
                ],
                is_valid=True
            )
        ]
        
        self._windows = [
            OperationalWindow(
                window_id="WIN-001",
                section_id="SEC-002",
                interval=TimeInterval(start=now, end=now + timedelta(hours=4)),
                availability=WindowAvailability.MAINTENANCE,
                max_trains=0,
                currently_assigned_trains=0
            )
        ]
        
        self._impacts = [
            TrainImpact(
                train_id="TRN-500",
                block_id="WIN-001",
                impact_type=ImpactType.DELAY,
                delay_minutes=45,
                is_rerouted=False,
                is_cancelled=False,
                severity=RiskLevel.MEDIUM,
                reason="Maintenance block on SEC-002",
                cascading_delay_minutes=15
            )
        ]

    def get_all_trains(self, page: int, page_size: int) -> tuple[List[Train], int]:
        start = (page - 1) * page_size
        end = start + page_size
        return self._trains[start:end], len(self._trains)

    def get_train_by_id(self, train_id: str) -> Optional[Train]:
        return next((t for t in self._trains if t.service.train_id == train_id), None)

    def get_all_train_paths(self, page: int, page_size: int) -> tuple[List[TrainPath], int]:
        start = (page - 1) * page_size
        end = start + page_size
        return self._paths[start:end], len(self._paths)

    def get_all_operational_windows(self, page: int, page_size: int) -> tuple[List[OperationalWindow], int]:
        start = (page - 1) * page_size
        end = start + page_size
        return self._windows[start:end], len(self._windows)

    def get_all_train_impacts(self, page: int, page_size: int) -> tuple[List[TrainImpact], int]:
        start = (page - 1) * page_size
        end = start + page_size
        return self._impacts[start:end], len(self._impacts)
