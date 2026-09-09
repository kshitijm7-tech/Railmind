"""Pytest configuration for the engine test suite.

Bootstraps ``sys.path`` so the tests run from the repository root, from
``engine/``, or from an IDE without package installation.
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import pytest  # noqa: E402

from engine.constraints.engine import ConstraintEngine  # noqa: E402


@pytest.fixture
def engine() -> ConstraintEngine:
    return ConstraintEngine()
