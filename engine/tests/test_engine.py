"""E01 invariants: package hygiene and engine aggregation semantics."""

import inspect

import engine
from engine.constraints.base import ConstraintRule
from engine.constraints.engine import ConstraintEngine, default_rules
from engine.constraints.result import ConstraintEvaluation, EngineError
from engine.constraints.types import ConstraintType

from engine.tests.fixtures.hand_checkable import base_context, conflict_context
from engine.tests.helpers import result_for, status_map


class _StubRule(ConstraintRule):
    def __init__(self, rule_id, status, constraint_type, rule_version="1.0.0"):
        self.rule_id = rule_id
        self.rule_version = rule_version
        self.constraint_type = constraint_type
        self.status = status

    def evaluate(self, context):
        from engine.constraints._toolkit import make_result

        return make_result(self, self.status, "INFO", "stub", "stub")


# ---------------------------------------------------------------------------
# Package hygiene
# ---------------------------------------------------------------------------


def test_package_imports_cleanly():
    assert engine.ENGINE_VERSION == "0.1.0"
    assert engine.CONSTRAINT_SET_ID == "railmind-core-constraints"


def test_default_rule_set_contains_9_hard_and_4_soft():
    rules = default_rules()
    hard = [r for r in rules if r.constraint_type is ConstraintType.HARD]
    soft = [r for r in rules if r.constraint_type is ConstraintType.SOFT]
    assert len(hard) == 9
    assert len(soft) == 4
    assert len({r.rule_id for r in rules}) == len(rules)


def test_no_rule_uses_forbidden_runtime_apis():
    """Determinism: rule modules must not touch clocks, randomness or I/O."""
    forbidden = ("datetime.now", "utcnow", "random.", "uuid.uuid4", "time.time")
    import engine.constraints.hard as hard_pkg
    import engine.constraints.soft as soft_pkg

    for module in list(hard_pkg.__dict__.values()) + list(soft_pkg.__dict__.values()):
        if inspect.ismodule(module) and module.__name__.startswith("engine.constraints"):
            source = inspect.getsource(module)
            for token in forbidden:
                assert token not in source, f"{module.__name__} uses forbidden API {token!r}"


# ---------------------------------------------------------------------------
# Aggregation / feasibility semantics
# ---------------------------------------------------------------------------


def test_base_fixture_all_pass_and_feasible(engine):
    evaluation = engine.evaluate(base_context())
    assert evaluation.feasible is True
    assert evaluation.hard_failures == []
    assert all(r.status == "PASS" for r in evaluation.results)


def test_conflict_fixture_infeasible_only_via_exclusivity(engine):
    evaluation = engine.evaluate(conflict_context())
    statuses = status_map(evaluation)
    assert evaluation.feasible is False
    assert statuses["RAILMIND.HARD.SECTION_EXCLUSIVITY"] == "FAIL"
    others = [s for rid, s in statuses.items() if rid != "RAILMIND.HARD.SECTION_EXCLUSIVITY"]
    assert all(s != "FAIL" for s in others)


def test_soft_warning_alone_keeps_candidate_feasible():
    soft_warning = _StubRule("X.SOFT.W", "WARNING", ConstraintType.SOFT)
    soft_pass = _StubRule("X.SOFT.P", "PASS", ConstraintType.SOFT)
    eng = ConstraintEngine(rules=[soft_warning, soft_pass])
    evaluation = eng.evaluate(base_context())
    assert evaluation.feasible is True
    assert len(evaluation.warnings) == 1


def test_hard_failure_makes_candidate_infeasible():
    hard_fail = _StubRule("X.HARD.F", "FAIL", ConstraintType.HARD)
    soft_warning = _StubRule("X.SOFT.W", "WARNING", ConstraintType.SOFT)
    eng = ConstraintEngine(rules=[hard_fail, soft_warning])
    evaluation = eng.evaluate(base_context())
    assert evaluation.feasible is False
    assert [r.rule_id for r in evaluation.hard_failures] == ["X.HARD.F"]


def test_multiple_hard_failures_are_all_collected():
    fail_a = _StubRule("X.HARD.A", "FAIL", ConstraintType.HARD)
    fail_b = _StubRule("X.HARD.B", "FAIL", ConstraintType.HARD)
    pass_c = _StubRule("X.HARD.C", "PASS", ConstraintType.HARD)
    eng = ConstraintEngine(rules=[fail_a, fail_b, pass_c])
    evaluation = eng.evaluate(base_context())
    assert evaluation.feasible is False
    assert {r.rule_id for r in evaluation.hard_failures} == {"X.HARD.A", "X.HARD.B"}


def test_duplicate_rule_id_rejected():
    a = _StubRule("X.HARD.A", "PASS", ConstraintType.HARD)
    b = _StubRule("X.HARD.A", "PASS", ConstraintType.HARD)
    try:
        ConstraintEngine(rules=[a, b])
    except EngineError as exc:
        assert "duplicate rule_id" in str(exc)
    else:
        raise AssertionError("duplicate rule_id accepted")


def test_result_identity_is_stamped_by_engine():
    sentinel = _StubRule("X.HARD.S", "PASS", ConstraintType.HARD)

    class _Impostor(_StubRule):
        def evaluate(self, context):
            result = super().evaluate(context)
            return result.model_copy(update={"rule_id": "NOT.ME"})

    eng = ConstraintEngine(rules=[sentinel])
    eng.evaluate(base_context())  # OK

    impostor_engine = ConstraintEngine(rules=[_Impostor("X.HARD.S", "PASS", ConstraintType.HARD)])
    try:
        impostor_engine.evaluate(base_context())
    except EngineError as exc:
        assert "NOT.ME" in str(exc)
    else:
        raise AssertionError("impostor result identity accepted")


def test_evaluation_is_deterministic(engine):
    ctx = base_context()
    first = engine.evaluate(ctx)
    second = engine.evaluate(base_context())
    assert first.model_dump() == second.model_dump()
    assert [r.rule_id for r in first.results] == [r.rule_id for r in second.results]


def test_evaluation_carries_version_stamps(engine):
    evaluation = engine.evaluate(base_context())
    assert evaluation.constraint_set_id == "railmind-core-constraints"
    assert evaluation.constraint_set_version == "1.0.0"
    assert evaluation.engine_version == "0.1.0"
    for result in evaluation.results:
        assert result.constraint_set_version == "1.0.0"
        assert result.rule_version == "1.0.0"


def test_result_for_helper_raises_for_unknown_rule(engine):
    evaluation = engine.evaluate(base_context())
    try:
        result_for(evaluation, "RAILMIND.HARD.NOT_A_RULE")
    except AssertionError as exc:
        assert "no result for rule" in str(exc)
    else:
        raise AssertionError("missing rule not detected")
