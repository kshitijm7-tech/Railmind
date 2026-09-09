"""Model-registry metadata contract (TRD §18) — E06.

TRD §18: "ML Model Registry — each model stores: model_id, model_name,
model_type, version, training_dataset_version, feature_schema_version,
training_timestamp, metrics, artifact_location, status."

The Tier-1 registry described there is database-backed; the engine boundary
owns only the metadata contract. No persistence, no MLflow, no artifact
loading — those stay outside the engine (prompt §41). The fields exist so the
backend registry and every prediction result can speak one vocabulary.

This module is deliberately data-only (frozen pydantic, no I/O): the same
discipline as E02–E05 configuration.
"""

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class ModelStatus(str, Enum):
    """TRD §18 registry status (example shows ``status: ACTIVE``)."""

    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    ARCHIVED = "ARCHIVED"


class ModelMetadata(BaseModel):
    """TRD §18 registry record, as a frozen value object.

    ``training_dataset_version`` / ``training_timestamp`` / ``artifact_location``
    are None for rule-based deterministic baselines (there is no training run
    to cite) — ``status`` then records the honest DISABLED state and
    ``deterministic_fallback`` documents the TRD §50 degradation chain.
    """

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    model_id: str
    model_name: str
    model_type: str  # e.g. DURATION_REGRESSION | FAILURE_RISK_CLASSIFICATION
    version: str
    feature_schema_version: str
    algorithm: str  # e.g. XGBoost | deterministic-rules
    training_dataset_version: Optional[str] = None
    training_timestamp: Optional[str] = None
    metrics: Dict[str, float] = Field(default_factory=dict)
    artifact_location: Optional[str] = None
    status: ModelStatus = ModelStatus.DISABLED
    deterministic_fallback: bool = False

    @property
    def identity(self) -> str:
        """``model_id@version`` — the string used in prediction provenance."""
        return f"{self.model_id}@{self.version}"


def feature_schema_version() -> str:
    """Version of the E06 feature contracts defined in ``inputs.py``.

    Bump when the feature schema changes so registry records can pin the
    exact schema a model was trained/served against (TRD §18).
    """
    return "1.0.0"


__all__ = ["ModelMetadata", "ModelStatus", "feature_schema_version"]
