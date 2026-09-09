"""The common model interface (TRD §17) — E06's architectural core.

TRD §17 mandates that every predictive model implement one common interface:

    class PredictionModel(Protocol):
        def predict(self, features): ...
        def predict_with_uncertainty(self, features): ...
        def get_version(self): ...
        def explain(self, features): ...

so that XGBoost can later be replaced by LightGBM, PyTorch or a GNN without
changing the rest of RAILMIND. This module defines that contract as a typing
``Protocol`` plus the shared errors and identity contract.

Concrete predictors (TRD §13 duration regression, TRD §15 failure-risk
classification) implement this protocol in their own modules. The interface
layer knows nothing about any ML library: everything crossing the boundary is
plain engine domain data.
"""

from typing import Any, Dict, Protocol, runtime_checkable

from engine._version import ENGINE_VERSION


class ModelNotAvailableError(RuntimeError):
    """Raised when a caller requires a trained ML model that does not exist.

    TRD §50 makes the deterministic fallback the graceful-degradation path;
    this error exists for callers that explicitly demand model-backed
    inference (e.g. after loading a trained artifact) and must not receive
    baseline numbers dressed up as ML output.
    """


class ModelPredictionError(ValueError):
    """Raised when a predictor cannot produce a valid prediction.

    Mirrors E01–E05's loud failure discipline: malformed features, violated
    invariants or non-finite model output are rejected at the boundary —
    never silently clamped, defaulted or dropped.
    """


@runtime_checkable
class PredictionModel(Protocol):
    """TRD §17 common model interface.

    Implementations are deterministic, immutable components. ``features`` is
    the predictor's own frozen input contract (never a generic dict), and
    ``predict`` returns the predictor's frozen result contract with probability
    outputs bounded to [0, 1].
    """

    def predict(self, features: Any) -> Any:
        """Point prediction (deterministic)."""
        ...

    def predict_with_uncertainty(self, features: Any) -> Any:
        """Prediction with the model's uncertainty evidence attached."""
        ...

    def get_version(self) -> str:
        """Model version string (registry identity, TRD §18)."""
        ...

    def explain(self, features: Any) -> Dict[str, Any]:
        """Deterministic, data-derived explanation evidence."""
        ...


def model_identity(model_id: str, model_version: str) -> Dict[str, str]:
    """Uniform provenance dict stamped onto every prediction result."""
    return {
        "model_id": model_id,
        "model_version": model_version,
        "engine_version": ENGINE_VERSION,
    }


def require_probability(value: float, field_name: str) -> float:
    """Probability-boundary defense: finite and inside [0, 1], else reject.

    NaN and ±Infinity fail the range checks (all comparisons with NaN are
    False). No clamping — the engine fails loudly rather than returning
    corrupt decision evidence (prompt §20/§8).
    """
    if value < 0.0 or value > 1.0:
        raise ModelPredictionError(
            f"{field_name} must be within [0, 1]; got {value!r}"
        )
    return value


def require_finite(value: float, field_name: str) -> float:
    """Reject NaN and ±Infinity at every numerical prediction boundary."""
    if value != value:  # NaN is the only value not equal to itself
        raise ModelPredictionError(f"{field_name} must be finite; got NaN")
    if value in (float("inf"), float("-inf")):
        raise ModelPredictionError(
            f"{field_name} must be finite; got {value!r}"
        )
    return value


__all__ = [
    "PredictionModel",
    "ModelNotAvailableError",
    "ModelPredictionError",
    "model_identity",
    "require_probability",
    "require_finite",
]
