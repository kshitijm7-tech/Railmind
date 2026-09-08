"""Tests — HARD rule: track occupancy / section exclusivity."""

from engine.constraints.hard.track_occupancy import TrackOccupancyRule
from engine.models.context import ConstraintContext
from engine.models.inputs import CandidateBlock, SectionOccupancy, TimeInterval

from engine.tests.helpers import t, t_next


def block(start, end, section_id="SEC-01") -> CandidateBlock:
    return CandidateBlock(section_id=section_id, interval=TimeInterval(start=start, end=end))


def occupancy(occ_id, start, end, section_id="SEC-01", kind="MAINTENANCE") -> SectionOccupancy:
    return SectionOccupancy(
        occupancy_id=occ_id, section_id=section_id, interval=TimeInterval(start=start, end=end), kind=kind
    )


def evaluate(block_obj, *occupancies) -> object:
    context = ConstraintContext(candidate_block=block_obj, section_occupancies=list(occupancies))
    return TrackOccupancyRule().evaluate(context)


def test_same_section_overlap_fails():
    # Occupancy 10:00–11:00, block 10:30–11:30 → FAIL
    result = evaluate(block(t(10, 30), t(11, 30)), occupancy("OCC-1", t(10), t(11)))
    assert result.status == "FAIL"
    assert result.violation_degree == 30.0


def test_same_section_adjacent_passes():
    result = evaluate(block(t(11), t(12)), occupancy("OCC-1", t(10), t(11)))
    assert result.status == "PASS"


def test_different_section_overlap_is_not_a_conflict():
    result = evaluate(block(t(10, 30), t(11, 30)), occupancy("OCC-1", t(10), t(11), section_id="SEC-02"))
    assert result.status == "PASS"


def test_free_section_passes_with_checked_count():
    result = evaluate(block(t(10), t(11)), occupancy("OCC-1", t(12), t(13)))
    assert result.status == "PASS"
    assert "1 occupancy record" in result.explanation


def test_no_occupancy_data_passes():
    result = evaluate(block(t(10), t(11)))
    assert result.status == "PASS"


def test_multiple_overlapping_occupancies_sorted():
    result = evaluate(
        block(t(10), t(12)),
        occupancy("OCC-B", t(11), t(12)),
        occupancy("OCC-A", t(10), t(11)),
    )
    assert result.status == "FAIL"
    sources = [e.source for e in result.evidence if e.source.startswith("occupancy:")]
    assert sources == ["occupancy:OCC-A", "occupancy:OCC-B"]
