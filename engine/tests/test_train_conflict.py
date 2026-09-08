"""Tests — HARD rule: train-path conflicts (strict overlap semantics)."""

from engine.constraints.hard.train_conflict import TrainConflictRule
from engine.models.context import ConstraintContext
from engine.models.inputs import CandidateBlock, PathSegmentRef, TimeInterval, TrainPathRef

from engine.tests.helpers import t, t_next


def block(start, end, section_id="SEC-01") -> CandidateBlock:
    return CandidateBlock(section_id=section_id, interval=TimeInterval(start=start, end=end))


def train(train_id, start, end, section_id="SEC-01") -> TrainPathRef:
    return TrainPathRef(
        train_id=train_id,
        segments=[PathSegmentRef(section_id=section_id, interval=TimeInterval(start=start, end=end))],
    )


def evaluate(block_obj, *trains) -> object:
    context = ConstraintContext(candidate_block=block_obj, train_paths=list(trains))
    return TrainConflictRule().evaluate(context)


def test_no_overlap_passes():
    # Train 10:00–10:30, block 10:30–11:30 → adjacent, PASS
    result = evaluate(block(t(10, 30), t(11, 30)), train("TRN-1", t(10), t(10, 30)))
    assert result.status == "PASS"


def test_partial_overlap_fails():
    # Train 10:00–10:30, block 10:20–11:30 → 10 min conflict
    result = evaluate(block(t(10, 20), t(11, 30)), train("TRN-1", t(10), t(10, 30)))
    assert result.status == "FAIL"
    assert result.violation_degree == 10.0


def test_exact_same_interval_fails():
    result = evaluate(block(t(10), t(10, 30)), train("TRN-1", t(10), t(10, 30)))
    assert result.status == "FAIL"
    assert result.violation_degree == 30.0


def test_train_completely_inside_block_fails():
    result = evaluate(
        block(t(10), t(12)),
        train("TRN-1", t(10, 30), t(11)),
    )
    assert result.status == "FAIL"
    assert result.violation_degree == 30.0


def test_block_completely_inside_train_fails():
    result = evaluate(
        block(t(10, 30), t(11)),
        train("TRN-1", t(10), t(12)),
    )
    assert result.status == "FAIL"
    assert result.violation_degree == 30.0


def test_adjacent_intervals_on_both_sides_pass():
    # Train ends at block start; second train starts at block end.
    result = evaluate(
        block(t(10, 30), t(11, 30)),
        train("TRN-1", t(10), t(10, 30)),
        train("TRN-2", t(11, 30), t(12)),
    )
    assert result.status == "PASS"


def test_train_on_other_section_is_not_a_conflict():
    # Overlapping times but different section → PASS
    result = evaluate(
        block(t(10), t(11)),
        train("TRN-1", t(10), t(11), section_id="SEC-02"),
    )
    assert result.status == "PASS"


def test_multiple_conflicting_trains_reported_deterministically():
    result = evaluate(
        block(t(10), t(12)),
        train("TRN-2", t(11), t(12)),
        train("TRN-1", t(10), t(11)),
    )
    assert result.status == "FAIL"
    sources = [e.source for e in result.evidence if e.source.startswith("train:")]
    assert sources == ["train:TRN-1", "train:TRN-2"]  # sorted, not input order
