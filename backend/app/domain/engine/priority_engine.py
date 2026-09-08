"""
P10 Priority Engine — Deterministic Maintenance Priority Scoring
================================================================
Each factor produces a normalized contribution (0.0-1.0) multiplied
by a configured weight. The final score is sum(contributions) * 100.

Weights must sum to 1.0.

Factor              Weight   Source
-----------         ------   ------
Criticality         0.25     task.criticality / defect.criticality
Defect Severity     0.20     defect.severity (if linked defect provided)
Safety Critical     0.20     defect.is_safety_critical
Urgency             0.15     defect.urgency_hours
Train Impact        0.10     number of affected train impacts
Task Type           0.05     EMERGENCY > CORRECTIVE > ...
Duration Overhead   0.05     task.duration.expected (longer = more disruptive)
"""
from typing import List, Optional
from datetime import datetime, timezone
from app.domain.engine.priority_models import (
    PriorityClass, PriorityFactorResult, PriorityResult
)
from app.domain.models.maintenance import MaintenanceTask, Defect
from app.domain.enums import Criticality, DefectSeverity, TaskType

ENGINE_VERSION = "1.0.0-deterministic"

# ── Factor weights (must sum to 1.0) ──────────────────────────────────────────
WEIGHTS = {
    "criticality":      0.25,
    "defect_severity":  0.20,
    "safety_critical":  0.20,
    "urgency":          0.15,
    "train_impact":     0.10,
    "task_type":        0.05,
    "duration":         0.05,
}

# ── Normalization maps ─────────────────────────────────────────────────────────
_CRITICALITY_SCORE = {
    Criticality.LOW:      0.10,
    Criticality.MEDIUM:   0.40,
    Criticality.HIGH:     0.75,
    Criticality.CRITICAL: 1.00,
}

_SEVERITY_SCORE = {
    DefectSeverity.MINOR:    0.10,
    DefectSeverity.MODERATE: 0.40,
    DefectSeverity.SEVERE:   0.75,
    DefectSeverity.CRITICAL: 1.00,
}

_TASK_TYPE_SCORE = {
    TaskType.EMERGENCY:   1.00,
    TaskType.CORRECTIVE:  0.75,
    TaskType.REPAIR:      0.60,
    TaskType.REPLACEMENT: 0.50,
    TaskType.PREVENTIVE:  0.30,
    TaskType.INSPECTION:  0.10,
}

def _clamp(v: float) -> float:
    return max(0.0, min(1.0, v))

def _urgency_normalized(urgency_hours: int) -> float:
    """Lower urgency_hours → higher score. 0 h = 1.0, >= 72 h = 0.0."""
    if urgency_hours <= 0:
        return 1.00
    if urgency_hours >= 72:
        return 0.00
    return _clamp(1.0 - urgency_hours / 72.0)

def _duration_normalized(expected_minutes: float) -> float:
    """Longer blocks are more disruptive. 0 min = 0.0, >= 480 min (8 h) = 1.0."""
    return _clamp(expected_minutes / 480.0)

def _train_impact_normalized(num_impacts: int) -> float:
    """0 = 0.0, >= 5 = 1.0, linear in between."""
    return _clamp(num_impacts / 5.0)


# ── Individual factor evaluators ──────────────────────────────────────────────

def _factor_criticality(task: MaintenanceTask, defect: Optional[Defect]) -> PriorityFactorResult:
    # Use the higher of task criticality and defect criticality (if available)
    task_score = _CRITICALITY_SCORE.get(task.criticality, 0.40)
    defect_score = _CRITICALITY_SCORE.get(defect.criticality, 0.0) if defect else None

    if defect_score is not None and defect_score > task_score:
        raw = f"Defect criticality={defect.criticality.value} (overrides task criticality={task.criticality.value})"
        nv = defect_score
    else:
        raw = f"Task criticality={task.criticality.value}"
        nv = task_score

    weight = WEIGHTS["criticality"]
    return PriorityFactorResult(
        factor_id="criticality",
        factor_name="Asset / Task Criticality",
        raw_value=raw,
        normalized_value=nv,
        weight=weight,
        contribution=nv * weight,
        explanation=f"Criticality level contributes {nv * weight * 100:.1f}% to overall priority.",
        evidence={"task_criticality": task.criticality.value,
                   "defect_criticality": defect.criticality.value if defect else None},
    )


def _factor_defect_severity(defect: Optional[Defect]) -> PriorityFactorResult:
    weight = WEIGHTS["defect_severity"]
    if defect is None:
        return PriorityFactorResult(
            factor_id="defect_severity",
            factor_name="Defect Severity",
            raw_value="No linked defect",
            normalized_value=0.0,
            weight=weight,
            contribution=0.0,
            explanation="No linked defect available; factor not scored.",
            evidence=None,
        )
    nv = _SEVERITY_SCORE.get(defect.severity, 0.40)
    return PriorityFactorResult(
        factor_id="defect_severity",
        factor_name="Defect Severity",
        raw_value=defect.severity.value,
        normalized_value=nv,
        weight=weight,
        contribution=nv * weight,
        explanation=f"Defect severity '{defect.severity.value}' contributes {nv * weight * 100:.1f}%.",
        evidence={"defect_id": defect.defect_id, "severity": defect.severity.value},
    )


def _factor_safety(defect: Optional[Defect]) -> PriorityFactorResult:
    weight = WEIGHTS["safety_critical"]
    if defect is None:
        return PriorityFactorResult(
            factor_id="safety_critical",
            factor_name="Safety Criticality",
            raw_value=False,
            normalized_value=0.0,
            weight=weight,
            contribution=0.0,
            explanation="No defect linked; safety flag not applicable.",
        )
    nv = 1.0 if defect.is_safety_critical else 0.0
    return PriorityFactorResult(
        factor_id="safety_critical",
        factor_name="Safety Criticality",
        raw_value=defect.is_safety_critical,
        normalized_value=nv,
        weight=weight,
        contribution=nv * weight,
        explanation=(
            "Safety-critical defect; maximum contribution applied."
            if defect.is_safety_critical
            else "Non-safety-critical defect; zero contribution from this factor."
        ),
        evidence={"defect_id": defect.defect_id, "is_safety_critical": defect.is_safety_critical},
    )


def _factor_urgency(defect: Optional[Defect]) -> PriorityFactorResult:
    weight = WEIGHTS["urgency"]
    if defect is None:
        return PriorityFactorResult(
            factor_id="urgency",
            factor_name="Urgency",
            raw_value="No defect — urgency unknown",
            normalized_value=0.0,
            weight=weight,
            contribution=0.0,
            explanation="No linked defect; urgency cannot be determined.",
        )
    nv = _urgency_normalized(defect.urgency_hours)
    return PriorityFactorResult(
        factor_id="urgency",
        factor_name="Urgency",
        raw_value=f"{defect.urgency_hours}h",
        normalized_value=nv,
        weight=weight,
        contribution=nv * weight,
        explanation=f"Defect must be addressed within {defect.urgency_hours}h; normalized urgency={nv:.2f}.",
        evidence={"urgency_hours": defect.urgency_hours},
    )


def _factor_train_impact(num_impacts: int) -> PriorityFactorResult:
    nv = _train_impact_normalized(num_impacts)
    weight = WEIGHTS["train_impact"]
    return PriorityFactorResult(
        factor_id="train_impact",
        factor_name="Train Impact",
        raw_value=num_impacts,
        normalized_value=nv,
        weight=weight,
        contribution=nv * weight,
        explanation=f"{num_impacts} train path(s) affected by this maintenance task.",
        evidence={"affected_train_count": num_impacts},
    )


def _factor_task_type(task: MaintenanceTask) -> PriorityFactorResult:
    nv = _TASK_TYPE_SCORE.get(task.type, 0.40)
    weight = WEIGHTS["task_type"]
    return PriorityFactorResult(
        factor_id="task_type",
        factor_name="Task Type",
        raw_value=task.type.value,
        normalized_value=nv,
        weight=weight,
        contribution=nv * weight,
        explanation=f"Task type '{task.type.value}' normalized score={nv:.2f}.",
        evidence={"task_type": task.type.value},
    )


def _factor_duration(task: MaintenanceTask) -> PriorityFactorResult:
    expected = task.duration.expected
    nv = _duration_normalized(expected)
    weight = WEIGHTS["duration"]
    return PriorityFactorResult(
        factor_id="duration",
        factor_name="Block Duration Overhead",
        raw_value=f"{expected}min",
        normalized_value=nv,
        weight=weight,
        contribution=nv * weight,
        explanation=f"Required duration {expected}min; longer tasks carry higher disruption overhead.",
        evidence={"expected_minutes": expected},
    )


# ── Priority class thresholds (score 0–100) ───────────────────────────────────
def _class_from_score(score: float) -> PriorityClass:
    if score >= 75:
        return PriorityClass.CRITICAL
    if score >= 55:
        return PriorityClass.HIGH
    if score >= 30:
        return PriorityClass.MEDIUM
    return PriorityClass.LOW


# ── Public engine ─────────────────────────────────────────────────────────────

class DeterministicPriorityEngine:
    """
    Deterministic Maintenance Priority Engine.

    For the same input state this engine always produces the same result.
    This is the P10 baseline. A future ML engine can implement the same
    evaluate() interface and be swapped in without API changes.
    """

    def evaluate(
        self,
        task: MaintenanceTask,
        defect: Optional[Defect] = None,
        num_train_impacts: int = 0,
        data_state: str = "MOCKED",
    ) -> PriorityResult:
        factors: List[PriorityFactorResult] = [
            _factor_criticality(task, defect),
            _factor_defect_severity(defect),
            _factor_safety(defect),
            _factor_urgency(defect),
            _factor_train_impact(num_train_impacts),
            _factor_task_type(task),
            _factor_duration(task),
        ]

        raw_score = sum(f.contribution for f in factors)   # 0.0 – 1.0
        score = round(raw_score * 100, 2)
        priority_class = _class_from_score(score)

        # Build human-readable explanation from significant contributors
        primary = [f for f in factors if f.contribution >= 0.05]
        drivers = ", ".join(f.factor_name for f in primary) if primary else "No dominant factor"
        explanation = (
            f"Priority: {priority_class.value} (score {score}/100). "
            f"Primary drivers: {drivers}."
        )

        return PriorityResult(
            task_id=task.task_id,
            score=score,
            priority_class=priority_class,
            factors=factors,
            explanation=explanation,
            engine_version=ENGINE_VERSION,
            calculated_at=datetime.now(timezone.utc),
            data_state=data_state,
        )