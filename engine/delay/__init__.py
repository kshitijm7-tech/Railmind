"""§16.3 train-delay / impact prediction (E09) — Model 3's Tier-1 baseline.

Authoritative shape (blueprint §16.3): direct delay per affected train plus a
simple graph-propagation pass over the section-adjacency graph for
downstream/cascading delay. Blueprint §16.4 explicitly mandates this
NetworkX-style adjacency baseline *first* ("explainable and always finishes
on time"); the GNN remains a deferred stretch goal (§16.4), not E09 scope.

No trained Model 3 artifact exists in the repository, so — exactly like E06's
deterministic baselines and per TRD §50/§51 — this package implements the
deterministic fallback as a first-class model behind the common TRD §17
``PredictionModel`` interface, honestly labeled
``deterministic-rules-graph-propagation``. The trained GBT (§16.3) is a later
artifact implementing the same interface.

This package is stdlib + pydantic only — it never imports ortools. The
adjacency walk is a plain breadth-first search; NetworkX is not required for
the baseline and the engine's determinism contract forbids nothing here, but
keeping the dependency out of the hot path keeps the package importable in
minimal environments (TRD §16 keeps networkx out of the deterministic rules
layer; §36 assigns it to the graph capability).
"""

from engine.delay.configuration import DelayModelConfig
from engine.delay.inputs import AffectedTrain, DelayFeatures
from engine.delay.model import GraphPropagationDelayModel
from engine.delay.result import (
    CLASS_CASCADING,
    CLASS_DIRECT,
    CLASS_UNAFFECTED,
    DELAY_ALGORITHM,
    DelayPredictionResult,
    TrainDelayRecord,
)

__all__ = [
    "DelayModelConfig",
    "AffectedTrain",
    "DelayFeatures",
    "GraphPropagationDelayModel",
    "DelayPredictionResult",
    "TrainDelayRecord",
    "CLASS_DIRECT",
    "CLASS_CASCADING",
    "CLASS_UNAFFECTED",
    "DELAY_ALGORITHM",
]
