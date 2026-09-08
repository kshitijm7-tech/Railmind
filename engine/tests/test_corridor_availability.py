"""Tests — HARD rule: corridor availability (canonical membership, fail-closed)."""

from engine.constraints.hard.corridor_availability import CorridorAvailabilityRule
from engine.models.context import ConstraintContext
from engine.models.inputs import CandidateBlock, CorridorState, SectionState, SectionStatus, TimeInterval

from engine.tests.helpers import t, t_next


def block(section_id="SEC-01") -> CandidateBlock:
    return CandidateBlock(section_id=section_id, interval=TimeInterval(start=t(21), end=t(23)))


def evaluate(block_obj, states, corridors) -> object:
    context = ConstraintContext(
        candidate_block=block_obj, section_states=states, corridors=corridors
    )
    return CorridorAvailabilityRule().evaluate(context)


def test_open_section_in_available_corridor_passes():
    result = evaluate(
        block(),
        [SectionState(section_id="SEC-01", status=SectionStatus.OPEN)],
        [CorridorState(corridor_id="CORR-07", section_ids=["SEC-01"], is_available=True)],
    )
    assert result.status == "PASS"


def test_closed_section_fails():
    result = evaluate(
        block(),
        [SectionState(section_id="SEC-01", status=SectionStatus.CLOSED)],
        [CorridorState(corridor_id="CORR-07", section_ids=["SEC-01"], is_available=True)],
    )
    assert result.status == "FAIL"
    assert result.severity.value == "CRITICAL"


def test_restricted_section_passes():
    # RESTRICTED is not CLOSED; availability limitation is not modeled at E01.
    result = evaluate(
        block(),
        [SectionState(section_id="SEC-01", status=SectionStatus.RESTRICTED)],
        [CorridorState(corridor_id="CORR-07", section_ids=["SEC-01"], is_available=True)],
    )
    assert result.status == "PASS"


def test_unavailable_corridor_fails():
    result = evaluate(
        block(),
        [SectionState(section_id="SEC-01", status=SectionStatus.OPEN)],
        [CorridorState(corridor_id="CORR-07", section_ids=["SEC-01"], is_available=False)],
    )
    assert result.status == "FAIL"
    assert "CORR-07" in result.explanation


def test_section_not_in_any_corridor_fails_closed():
    result = evaluate(
        block(),
        [SectionState(section_id="SEC-01", status=SectionStatus.OPEN)],
        [CorridorState(corridor_id="CORR-07", section_ids=["SEC-02"], is_available=True)],
    )
    assert result.status == "FAIL"
    assert "not a member" in result.explanation


def test_missing_section_state_fails_closed():
    result = evaluate(block(), [], [CorridorState(corridor_id="CORR-07", section_ids=["SEC-01"])])
    assert result.status == "FAIL"
    assert "fail-closed" in result.explanation
