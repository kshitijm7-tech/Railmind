"""Shared test helpers: fixed times, result lookup utilities."""

from datetime import datetime, timezone

from engine.constraints.result import ConstraintEvaluation, ConstraintResult


def t(hour: int, minute: int = 0) -> datetime:
    """Fixed timezone-aware time on 2026-09-14 (UTC)."""
    return datetime(2026, 9, 14, hour, minute, tzinfo=timezone.utc)


def t_next(hour: int, minute: int = 0) -> datetime:
    """Fixed timezone-aware time on 2026-09-15 (UTC)."""
    return datetime(2026, 9, 15, hour, minute, tzinfo=timezone.utc)


def result_for(evaluation: ConstraintEvaluation, rule_id: str) -> ConstraintResult:
    """Fetch one rule's result, failing loudly if absent."""
    for result in evaluation.results:
        if result.rule_id == rule_id:
            return result
    raise AssertionError(f"no result for rule {rule_id}; got {[r.rule_id for r in evaluation.results]}")


def status_map(evaluation: ConstraintEvaluation) -> dict:
    """Map rule_id → status for quick assertions."""
    return {r.rule_id: r.status for r in evaluation.results}
