"""Predictive Risk & Uncertainty Intelligence (E06) — blueprint §16, TRD §12–19.

This package owns the predictive-model boundary that E02 deliberately did not
implement: the common ``PredictionModel`` interface (TRD §17), duration
prediction (TRD §13 / blueprint §16.1), asset failure-risk prediction
(TRD §15) and the model-registry metadata contract (TRD §18).

No trained model artifact or dataset exists in this repository, so the only
shipped predictors are the TRD §50 deterministic fallbacks (rules / statistical
baseline). They are honest rule-based baselines — never presented as trained
ML. E02's weighted priority scoring (§16.2) is NOT reimplemented here: it
already lives in ``engine.priority`` (see docs/E02_Report.md).

Inference is fully deterministic: no clocks, no randomness, no network. The
dependency direction is E06 → (upstream contracts only); nothing in
engine.constraints/priority/optimization/scenario/simulation imports this
package (structurally tested).
"""

from engine.prediction.configuration import PredictionConfig, CRITICALITY_SCORES
from engine.prediction.duration import (
    DurationPredictor,
    duration_model_metadata,
    P10_FACTOR,
    P90_FACTOR,
)
from engine.prediction.failure_risk import (
    ASSET_TYPE_SCORES,
    FailureRiskPredictor,
    WEIGHTS,
    failure_risk_model_metadata,
)
from engine.prediction.inputs import (
    DurationFeatures,
    DurationPredictionWindow,
    FailureRiskFeatures,
    validate_duration_features,
    validate_failure_risk_features,
)
from engine.prediction.interface import (
    ModelNotAvailableError,
    ModelPredictionError,
    PredictionModel,
)
from engine.prediction.registry import (
    ModelMetadata,
    ModelStatus,
    feature_schema_version,
)
from engine.prediction.result import (
    DurationPredictionResult,
    FailureRiskPredictionResult,
    PredictionBase,
    PredictionProvenance,
)

__all__ = [
    # TRD §17 interface
    "PredictionModel",
    "ModelPredictionError",
    "ModelNotAvailableError",
    # TRD §18 registry
    "ModelMetadata",
    "ModelStatus",
    "feature_schema_version",
    # Inputs (TRD §13 / §15 feature vectors)
    "DurationFeatures",
    "DurationPredictionWindow",
    "FailureRiskFeatures",
    "validate_duration_features",
    "validate_failure_risk_features",
    # Predictors (TRD §50 deterministic fallbacks)
    "DurationPredictor",
    "duration_model_metadata",
    "P10_FACTOR",
    "P90_FACTOR",
    "FailureRiskPredictor",
    "failure_risk_model_metadata",
    "WEIGHTS",
    "ASSET_TYPE_SCORES",
    # Results (canonical TS prediction vocabulary)
    "DurationPredictionResult",
    "FailureRiskPredictionResult",
    "PredictionBase",
    "PredictionProvenance",
    # Configuration
    "PredictionConfig",
    "CRITICALITY_SCORES",
]