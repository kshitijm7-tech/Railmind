from typing import Protocol, List
from app.domain.engine.models import ConstraintSeverity, ConstraintViolation, EvaluationContext
from app.domain.models.planning import CandidateBlockWindow
from app.domain.models.common import TimeInterval
from datetime import time, datetime

class Rule(Protocol):
    rule_id: str
    severity: ConstraintSeverity

    def evaluate(self, candidate: CandidateBlockWindow, context: EvaluationContext) -> List[ConstraintViolation]:
        ...

class OperationalWindowRule:
    rule_id = "rule_operational_window"
    severity = ConstraintSeverity.HARD

    def evaluate(self, candidate: CandidateBlockWindow, context: EvaluationContext) -> List[ConstraintViolation]:
        violations = []
        c_start = candidate.interval.start
        c_end = candidate.interval.end
        
        # Check if candidate fits within any of the available windows
        fits = False
        for w in context.windows:
            if w.section_id != context.section_id:
                continue
            if c_start >= w.interval.start and c_end <= w.interval.end:
                fits = True
                break
        
        if not fits:
            violations.append(ConstraintViolation(
                rule_id=self.rule_id,
                severity=self.severity,
                message="Candidate interval does not fit within any operational window.",
                evidence={"start": c_start.isoformat(), "end": c_end.isoformat()}
            ))
        return violations

class MaintenanceDurationRule:
    rule_id = "rule_maintenance_duration"
    severity = ConstraintSeverity.HARD

    def evaluate(self, candidate: CandidateBlockWindow, context: EvaluationContext) -> List[ConstraintViolation]:
        duration_minutes = (candidate.interval.end - candidate.interval.start).total_seconds() / 60.0
        expected_duration = context.task.duration.expected
        if duration_minutes < expected_duration:
            return [ConstraintViolation(
                rule_id=self.rule_id,
                severity=self.severity,
                message=f"Candidate duration {duration_minutes}m is less than expected {expected_duration}m.",
                evidence={"candidate_duration": duration_minutes, "expected_duration": expected_duration}
            )]
        return []

class TrainPathConflictRule:
    rule_id = "rule_train_path_conflict"
    severity = ConstraintSeverity.HARD

    def evaluate(self, candidate: CandidateBlockWindow, context: EvaluationContext) -> List[ConstraintViolation]:
        violations = []
        c_start = candidate.interval.start
        c_end = candidate.interval.end

        for path in context.paths:
            for segment in path.segments:
                if segment.section_id == context.section_id:
                    s_start = segment.interval.start
                    s_end = segment.interval.end
                    # Overlap condition
                    if c_start < s_end and c_end > s_start:
                        violations.append(ConstraintViolation(
                            rule_id=self.rule_id,
                            severity=self.severity,
                            message=f"Conflict with train {path.train_id} on section {context.section_id}.",
                            evidence={
                                "train_id": path.train_id,
                                "train_start": s_start.isoformat(),
                                "train_end": s_end.isoformat()
                            }
                        ))
        return violations

class PreferredWindowRule:
    rule_id = "rule_preferred_window"
    severity = ConstraintSeverity.SOFT

    def evaluate(self, candidate: CandidateBlockWindow, context: EvaluationContext) -> List[ConstraintViolation]:
        # If candidate starts after 22:00, it's preferred. Otherwise issue a soft violation.
        c_start = candidate.interval.start
        # 22:00 is hour 22. So if hour < 22 and hour >= 6 for example. 
        # But let's just check if it's after 22:00
        # If candidate happens after 22:00, preferred.
        # This implies start_time time component >= 22:00 or something. 
        # But if it starts at 23:00, hour is 23. If it starts at 01:00, it's still night? 
        # Simple check: `c_start.hour >= 22 or c_start.hour < 6` (assuming night).
        # Let's just say `c_start.hour < 22` is a violation to keep it simple and literal.
        if c_start.hour < 22 and c_start.hour > 5:
            return [ConstraintViolation(
                rule_id=self.rule_id,
                severity=self.severity,
                message="Candidate is outside the preferred nighttime window (starts before 22:00).",
                evidence={"start_hour": c_start.hour}
            )]
        return []
