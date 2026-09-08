"""E05 contract tests: randomness containment and architecture boundaries.

Pins:
- ALL engine RNG lives inside engine.simulation.distributions (§6/§23/§45);
- dependency direction E05 → (nothing upstream it must re-derive); E01–E04
  never import E05;
- E02 priority / E03 objective / E04 ranking logic is never duplicated;
- provenance identity + serialization discipline match E01–E04 conventions.
"""

import ast
import inspect

import pytest

import engine
from engine._version import (
    ENGINE_VERSION,
    SIMULATION_MODEL_ID,
    SIMULATION_MODEL_VERSION,
)
from engine.simulation.simulator import derive_stream_seed


def _random_usage(module) -> list:
    """AST-level detection of real RNG usage (docstrings never match)."""
    tree = ast.parse(inspect.getsource(module))
    usages = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in node.names]
            if any("random" in n for n in names) or (
                isinstance(node, ast.ImportFrom) and node.module == "random"
            ):
                usages.append(f"import at line {node.lineno}")
        elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            if node.value.id == "random":
                usages.append(f"random.{node.attr} at line {node.lineno}")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "Random":
                usages.append(f"Random() call at line {node.lineno}")
    return usages


# ---------------------------------------------------------------------------
# §45 — Randomness containment: RNG only inside the simulation boundary
# ---------------------------------------------------------------------------


def test_rng_usage_is_confined_to_distributions_module():
    import engine.simulation.configuration as configuration
    import engine.simulation.distributions as distributions
    import engine.simulation.inputs as inputs
    import engine.simulation.result as result
    import engine.simulation.simulator as simulator

    # The designated randomness boundary must actually use the RNG.
    assert _random_usage(distributions), "sampling boundary lost its RNG?"
    # Every other E05 module must contain zero real RNG usage.
    for module in (configuration, inputs, result, simulator):
        usages = _random_usage(module)
        assert not usages, (
            f"{module.__name__} uses randomness outside the sampling "
            f"boundary: {usages}"
        )


def test_no_rng_leaks_into_deterministic_engines():
    """E01–E04 packages must remain free of any random-number usage."""
    import engine.constraints.hard as hard_pkg
    import engine.constraints.soft as soft_pkg
    import engine.optimization.evaluation as evaluation
    import engine.priority.engine as priority_engine
    import engine.scenario.comparison as comparison

    for module in (
        hard_pkg, soft_pkg, evaluation, priority_engine, comparison,
    ):
        usages = _random_usage(module)
        assert not usages, (
            f"{module.__name__} leaked randomness into a deterministic "
            f"layer: {usages}"
        )


def test_deterministic_engines_never_import_e05():
    """Dependency direction: nothing below E05 may import it."""
    import engine.optimization.evaluation
    import engine.priority.engine
    import engine.scenario.comparison
    import engine.scenario.result

    for module in (
        engine.optimization.evaluation,
        engine.priority.engine,
        engine.scenario.comparison,
        engine.scenario.result,
    ):
        source = inspect.getsource(module)
        assert "engine.simulation" not in source, (
            f"{module.__name__} illegally depends on E05"
        )


# ---------------------------------------------------------------------------
# §17/§18 — No duplication of E02/E03 logic
# ---------------------------------------------------------------------------


def test_e05_never_reimplements_upstream_engine_logic():
    import engine.simulation.simulator as simulator

    source = inspect.getsource(simulator)
    # Priority factors (E02) and objective terms (E03) must not appear.
    for token in ("criticality", "overdue_days", "failure_risk",
                  "train_delay_weight", "unscheduled_priority_weight",
                  "block_count_weight", "objective_weights"):
        assert token not in source, f"E05 duplicates upstream logic: {token!r}"


def test_e05_public_surface_does_not_expose_solver_or_persistence():
    """The E05 export set is exactly the documented public surface — no
    solver/persistence/API capability may ride along."""
    from engine.simulation import __all__ as e05_exports

    expected = {
        "SimulationConfig", "DurationDistribution", "DurationBand",
        "BlockWindow", "validate_block_windows", "simulate_block",
        "simulate_plan", "PlanSimulationResult", "BlockRiskProfile",
        "SampleSummary", "C6_DURATION_FEASIBILITY", "C7_WINDOW_BOUNDS",
    }
    assert set(e05_exports) == expected


# ---------------------------------------------------------------------------
# §33/§34 — Provenance and serialization discipline
# ---------------------------------------------------------------------------


def test_simulation_provenance_identity_is_declared():
    assert SIMULATION_MODEL_ID == "railmind-monte-carlo-robustness"
    assert SIMULATION_MODEL_VERSION == "1.0.0"
    assert engine.SIMULATION_MODEL_ID == SIMULATION_MODEL_ID


def test_result_carries_full_evidence_for_explainability():
    """§31: iterations/seed/distribution/threshold evidence must be present."""
    from datetime import datetime, timezone

    from engine.simulation import (
        BlockWindow, DurationBand, SimulationConfig, simulate_block,
    )

    w = BlockWindow(
        window_id="W-EV", section_id="SEC-EV",
        earliest_start=datetime(2026, 9, 14, 22, 0, tzinfo=timezone.utc),
        latest_end=datetime(2026, 9, 15, 2, 0, tzinfo=timezone.utc),
        max_duration_minutes=78.0,
        task_bands=[DurationBand(task_id="T1", p10_minutes=30.0, p90_minutes=50.0)],
    )
    result = simulate_block(w, SimulationConfig(iterations=40, seed=5))
    assert result.iterations == 40
    assert result.seed == derive_stream_seed(5, "W-EV")  # exact stream reported
    assert result.distribution == "UNIFORM"
    profile = result.block_profiles[0]
    assert set(profile.constraint_exceedances) == {
        "c6_duration_feasibility", "c7_window_bounds",
    }
    assert profile.violation_draws == sorted(profile.violation_draws)
    assert set(profile.violation_draws).issubset(range(40))


def test_engine_exports_expose_e05_public_surface():
    for name in ("SimulationConfig", "DurationDistribution", "DurationBand",
                 "BlockWindow", "validate_block_windows", "simulate_block",
                 "simulate_plan", "PlanSimulationResult", "BlockRiskProfile",
                 "SampleSummary", "SIMULATION_MODEL_ID", "SIMULATION_MODEL_VERSION"):
        assert name in engine.__all__, f"E05 export {name!r} missing"
    # Private sampling helpers stay internal.
    assert "make_rng" not in engine.__all__
    assert "sample_duration" not in engine.__all__
    assert "derive_stream_seed" not in engine.__all__
