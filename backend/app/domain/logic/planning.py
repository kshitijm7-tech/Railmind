from typing import List
from datetime import timedelta
from app.domain.models.maintenance import MaintenanceTask
from app.domain.models.operations import OperationalWindow, TrainPath
from app.domain.models.planning import CandidateBlockWindow
from app.domain.models.common import TimeInterval
from app.domain.enums import WindowAvailability

class CandidateGenerator:
    def generate_candidates(self, task: MaintenanceTask, windows: List[OperationalWindow]) -> List[CandidateBlockWindow]:
        candidates = []
        for window in windows:
            if window.section_id != task.section_id:
                continue
            if window.availability not in [WindowAvailability.AVAILABLE]:
                continue
            
            # Simple approach: Check if window is long enough
            window_duration = (window.interval.end - window.interval.start).total_seconds() / 60.0
            if window_duration >= task.duration.expected:
                # Propose start at window start
                cand_end = window.interval.start + timedelta(minutes=task.duration.expected)
                
                # Suitability score could be simple percentage of window consumed
                suitability = float(task.duration.expected) / window_duration * 100.0
                
                candidates.append(CandidateBlockWindow(
                    interval=TimeInterval(start=window.interval.start, end=cand_end),
                    suitability_score=suitability,
                    conflicts=[]
                ))
        return candidates

from app.domain.engine.core import ConstraintEngine
from app.domain.engine.rules import OperationalWindowRule, MaintenanceDurationRule, TrainPathConflictRule, PreferredWindowRule
from app.domain.engine.models import EvaluationContext

class ConflictDetector:
    def __init__(self):
        self.engine = ConstraintEngine([
            OperationalWindowRule(),
            MaintenanceDurationRule(),
            TrainPathConflictRule(),
            PreferredWindowRule()
        ])

    def detect_conflicts(self, candidate: CandidateBlockWindow, paths: List[TrainPath], section_id: str, task: MaintenanceTask, windows: List[OperationalWindow]) -> CandidateBlockWindow:
        context = EvaluationContext(
            task=task,
            windows=windows,
            paths=paths,
            section_id=section_id
        )
        result = self.engine.evaluate_candidate(candidate, context)
        
        # Map violations to conflicts for P07 compatibility, while also returning richer objects
        conflicts = [v.message for v in result.violations]
        
        return CandidateBlockWindow(
            interval=candidate.interval,
            suitability_score=candidate.suitability_score,
            conflicts=conflicts,
            violations=[v.model_dump() for v in result.violations]
        )
