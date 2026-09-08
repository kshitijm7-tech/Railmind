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

class ConflictDetector:
    def detect_conflicts(self, candidate: CandidateBlockWindow, paths: List[TrainPath], section_id: str) -> CandidateBlockWindow:
        conflicts = []
        c_start = candidate.interval.start
        c_end = candidate.interval.end
        
        for path in paths:
            for segment in path.segments:
                if segment.section_id == section_id:
                    s_start = segment.interval.start
                    s_end = segment.interval.end
                    
                    # Overlap condition
                    if c_start < s_end and c_end > s_start:
                        conflicts.append(f"Train {path.train_id} overlaps at section {section_id}")
        
        return CandidateBlockWindow(
            interval=candidate.interval,
            suitability_score=candidate.suitability_score,
            conflicts=conflicts
        )
