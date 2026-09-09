"""Explicit bridge from the backend package to the repository-root engine.

The RailMind engine (``engine/``) is a repository-root Python package,
independently tested (357 tests, E01–E06). It is not an installed dependency
of the backend — the backend venv's ``sys.path`` does not include the repo
root. This module performs the smallest explicit, documented bootstrap so the
backend can import engine **contracts only**.

Architectural rules (E07, prompt §3/§4/§26):

- the engine is the source of truth for ALL domain math; the backend wraps it,
  never duplicates it;
- only public engine surfaces are imported here (``engine`` top-level and its
  engine-internal subpackages) — never engine-private helpers;
- one-time, idempotent bootstrap at import: no repeated path manipulation, no
  global state beyond ``sys.path`` (which the interpreter itself owns).
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]

_ENGINE_ALREADY_IMPORTABLE = False
try:  # e.g. when the repo root is on sys.path (engine test runs, tooling)
    import engine  # noqa: F401

    _ENGINE_ALREADY_IMPORTABLE = True
except ModuleNotFoundError:
    pass

if not _ENGINE_ALREADY_IMPORTABLE:
    if not (_REPO_ROOT / "engine" / "__init__.py").exists():
        raise RuntimeError(
            "RailMind engine package not found at expected location "
            f"{_REPO_ROOT / 'engine'} — the backend adapter requires the "
            "engine source tree (E07 contract; see docs/E07_Report.md)"
        )
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))

# Public engine surface used by the E07 adapter. Contracts only — no private
# helpers, no engine-internal test utilities.
from engine import (  # noqa: E402
    AssetFailureRisk,
    BlockActivation,
    BlockWindow,
    CandidateSolution,
    DurationBand,
    DurationPredictor,
    ENGINE_VERSION,
    FailureRiskFeatures,
    FailureRiskPredictor,
    FailureRiskPredictionResult,
    DurationFeatures,
    DurationPredictionWindow,
    DurationPredictionResult,
    ObjectiveEvaluator,
    PlanSimulationResult,
    PredictionConfig,
    PriorityEngine,
    PriorityEngineConfig,
    PriorityInput,
    PriorityResult,
    SimulationConfig,
    TaskAssignment,
    simulate_plan,
)


def engine_health() -> dict:
    """Engine-side identity for /health and diagnostics (E07 §7/§23)."""
    return {"engine_version": ENGINE_VERSION, "phases": ["E01", "E02", "E03", "E04", "E05", "E06"]}


__all__ = [
    "engine_health",
    "ENGINE_VERSION",
    # E02
    "PriorityEngine",
    "PriorityEngineConfig",
    "PriorityInput",
    "PriorityResult",
    "AssetFailureRisk",
    # E03
    "ObjectiveEvaluator",
    "CandidateSolution",
    "TaskAssignment",
    "BlockActivation",
    # E05
    "SimulationConfig",
    "BlockWindow",
    "DurationBand",
    "PlanSimulationResult",
    "simulate_plan",
    # E06
    "DurationPredictor",
    "DurationFeatures",
    "DurationPredictionWindow",
    "DurationPredictionResult",
    "FailureRiskPredictor",
    "FailureRiskFeatures",
    "FailureRiskPredictionResult",
    "PredictionConfig",
]
