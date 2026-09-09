"""Tests — HARD rule: operational window containment (inclusive boundaries)."""

from datetime import timedelta

from engine.constraints.hard.operational_window import OperationalWindowRule
from engine.models.context import ConstraintContext
from engine.models.inputs import (
    CandidateBlock,
    OperationalWindowRef,
    TimeInterval,
    WindowAvailability,
)

from engine.tests.helpers import t, t_next


def window(section_id="SEC-01", start=None, end=None, window_id="WIN-A") -> OperationalWindowRef:
    return OperationalWindowRef(
        window_id=window_id,
        section_id=section_id,
        interval=TimeInterval(start=start or t(20), end=end or t_next(2)),
        availability=WindowAvailability.AVAILABLE,
    )


def block(start, end, section_id="SEC-01") -> CandidateBlock:
    return CandidateBlock(section_id=section_id, interval=TimeInterval(start=start, end=end))


def evaluate(block_obj, *windows) -> str:
    context = ConstraintContext(
        candidate_block=block_obj, operational_windows=list(windows)
    )
    return OperationalWindowRule().evaluate(context)


def test_fully_inside_passes():
    result = evaluate(block(t(21), t(23)), window())
    assert result.status == "PASS"


def test_starts_at_boundary_passes():
    # Block starts exactly at window start (inclusive boundary) → PASS
    result = evaluate(block(t(20), t(22)), window())
    assert result.status == "PASS"


def test_ends_at_boundary_passes():
    # Block ends exactly at window end (inclusive boundary) → PASS
    result = evaluate(block(t_next(0), t_next(2)), window())
    assert result.status == "PASS"


def test_starts_before_window_fails():
    result = evaluate(block(t(19), t(21)), window())
    assert result.status == "FAIL"
    assert result.violation_degree == 60.0  # 1 hour overshoot at start


def test_ends_after_window_fails():
    result = evaluate(block(t_next(1), t_next(3)), window())
    assert result.status == "FAIL"
    assert result.violation_degree == 60.0  # 1 hour overshoot at end


def test_no_window_for_section_fails_closed():
    # Block on SEC-02 but only a SEC-01 window supplied → fail closed
    result = evaluate(block(t(21), t(23), section_id="SEC-02"), window())
    assert result.status == "FAIL"
    assert "fail-closed" in result.explanation


def test_window_selection_is_deterministic_among_multiple():
    # Two windows on the same section; the one covering the block start wins.
    early = window(window_id="WIN-EARLY", start=t(18), end=t(20))
    late = window(window_id="WIN-LATE", start=t(20), end=t_next(2))
    result = evaluate(block(t(21), t(23)), early, late)
    assert result.status == "PASS"
    assert any("WIN-LATE" in e.source for e in result.evidence)


def test_wrong_section_window_ignored_when_matching_exists():
    other = window(section_id="SEC-02", window_id="WIN-B")
    matching = window(window_id="WIN-A")
    result = evaluate(block(t(21), t(23)), other, matching)
    assert result.status == "PASS"
