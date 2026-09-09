"""Engine adapter package (E07) — backend boundary to the RailMind engine.

This package is the ONLY place in the backend that imports the engine:
``router → EngineIntegrationService → engine contracts``. The engine owns all
domain math; nothing here re-implements E01–E06 logic (architecturally
tested in backend/tests/test_engine_architecture.py).
"""

from app.engine_adapter.mapper import (
    translate_engine_error,
    window_request_to_block_window,
    prioritize_task_to_priority_input,
)
from app.engine_adapter.service import EngineIntegrationService

__all__ = [
    "EngineIntegrationService",
    "translate_engine_error",
    "window_request_to_block_window",
    "prioritize_task_to_priority_input",
]
