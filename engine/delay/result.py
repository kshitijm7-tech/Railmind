"""Delay prediction results (E09) — per-train, explainable §16.3 output.

§16.3 output specification: "expected delay per affected train, confidence."
Every record carries the classification (direct / cascading / unaffected),
the propagation hop count, and the priority-protection factor applied, so
the delay is reproducible from the record alone (blueprint §21
explainability-by-construction). Unaffected trains are reported explicitly
with zero delay — never silently dropped.
"""

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict

from engine._version import DELAY_MODEL_ID, DELAY_MODEL_VERSION, ENGINE_VERSION

#: Train classification wrt the blocked section (documented semantics).
CLASS_DIRECT = "direct"
CLASS_CASCADING = "cascading"
CLASS_UNAFFECTED = "unaffected"

#: Honest algorithm label — no trained Model 3 artifact exists (TRD §50/§51).
DELAY_ALGORITHM = "deterministic-rules-graph-propagation"


class TrainDelayRecord(BaseModel):
    """One train's delay evidence for the proposed block window."""

    model_config = ConfigDict(frozen=True)

    train_id: str
    classification: str  # CLASS_DIRECT | CLASS_CASCADING | CLASS_UNAFFECTED
    delay_minutes: float  # >= 0.0
    # Adjacency hops from the blocked section to the train's route
    # (0 for direct, 1..max_propagation_depth for cascading, None if the
    # train's route is unreachable from the blocked section).
    propagation_hops: int = 0
    # Multiplier applied for priority protection (1.0 = no protection).
    priority_protection_factor: float = 1.0


class DelayPredictionResult(BaseModel):
    """§16.3 prediction for one proposed block window."""

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    window_id: str
    section_id: str
    trains: List[TrainDelayRecord] = []
    # Σ_r delay_r over affected trains (the §17.2 delay_pred aggregation view).
    total_delay_minutes: float
    # §16.3 output: confidence of the prediction.
    confidence: float

    algorithm: str = DELAY_ALGORITHM
    model_id: str = DELAY_MODEL_ID
    model_version: str = DELAY_MODEL_VERSION
    engine_version: str = ENGINE_VERSION

    def delay_for(self, train_id: str) -> float:
        """Per-train lookup (exact §17.2 delay_pred(w, r) view)."""
        for record in self.trains:
            if record.train_id == train_id:
                return record.delay_minutes
        raise KeyError(
            f"train {train_id!r} is not part of this delay prediction"
        )

    def explain(self) -> Dict[str, Any]:
        """Deterministic explanation evidence (blueprint §21)."""
        return {
            "window_id": self.window_id,
            "section_id": self.section_id,
            "total_delay_minutes": self.total_delay_minutes,
            "direct_trains": [
                r.train_id for r in self.trains if r.classification == CLASS_DIRECT
            ],
            "cascading_trains": [
                {
                    "train_id": r.train_id,
                    "hops": r.propagation_hops,
                    "delay_minutes": r.delay_minutes,
                }
                for r in self.trains
                if r.classification == CLASS_CASCADING
            ],
            "unaffected_trains": [
                r.train_id for r in self.trains if r.classification == CLASS_UNAFFECTED
            ],
            "confidence": self.confidence,
            "algorithm": self.algorithm,
            "model_id": self.model_id,
            "model_version": self.model_version,
            "engine_version": self.engine_version,
        }
