"""Shared rule toolkit: interval helpers, evidence/result builders.

Keeps rule implementations free of boilerplate and ensures every result is
constructed uniformly (status/severity/explanation/evidence discipline).
"""

from datetime import datetime
from typing import List, Optional, Tuple

from engine.models.context import ConstraintContext
from engine.constraints.base import ConstraintRule
from engine.constraints.result import ConstraintEvidence, ConstraintResult


def make_result(
    rule: ConstraintRule,
    status: str,
    severity: str,
    message: str,
    explanation: str,
    evidence: Optional[List[ConstraintEvidence]] = None,
    affected_entities: Optional[List[str]] = None,
    violation_degree: Optional[float] = None,
) -> ConstraintResult:
    """Uniformly stamp every result with the rule identity and set version."""
    return ConstraintResult(
        rule_id=rule.rule_id,
        rule_version=rule.rule_version,
        constraint_type=rule.constraint_type,
        status=status,
        severity=severity,
        message=message,
        explanation=explanation,
        evidence=evidence or [],
        affected_entities=affected_entities or [],
        violation_degree=violation_degree,
    )


def evidence(source: str, description: str, quantity: Optional[float] = None) -> ConstraintEvidence:
    return ConstraintEvidence(source=source, description=description, quantity=quantity)


def overlap_minutes(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> float:
    """Strict-overlap duration in minutes; touching endpoints overlap 0 minutes."""
    latest_start = max(a_start, b_start)
    earliest_end = min(a_end, b_end)
    if latest_start >= earliest_end:
        return 0.0
    return (earliest_end - latest_start).total_seconds() / 60.0


def block_on_section(context: ConstraintContext, section_id: str) -> bool:
    return context.candidate_block.section_id == section_id


def find_window(context: ConstraintContext):
    """Return the operational window declared for the candidate's section, or None."""
    section_id = context.candidate_block.section_id
    matches = [w for w in context.operational_windows if w.section_id == section_id]
    if not matches:
        return None
    # Deterministic selection: the window whose start is latest but not after
    # the block start; otherwise the first match in stable (input) order.
    best = None
    for window in matches:
        if window.interval.start <= context.candidate_block.interval.start:
            if best is None or window.interval.start > best.interval.start:
                best = window
    return best if best is not None else matches[0]


def find_section_state(context: ConstraintContext):
    section_id = context.candidate_block.section_id
    for state in context.section_states:
        if state.section_id == section_id:
            return state
    return None


def find_corridor(context: ConstraintContext, section_id: str):
    for corridor in context.corridors:
        if section_id in corridor.section_ids:
            return corridor
    return None


def max_task_minutes(context: ConstraintContext) -> Optional[Tuple[str, int]]:
    """Longest assigned task by expected duration (deterministic tie-break on task_id)."""
    if not context.tasks:
        return None
    best = min(
        context.tasks,
        key=lambda t: (-t.duration.expected, t.task_id),
    )
    return best.task_id, best.duration.expected
