"""§16.3 train-delay baseline (E09) — deterministic graph-propagation model.

Implements the blueprint §16.4-mandated NetworkX baseline "first": direct
delay for trains routed through the blocked section, plus a bounded
downstream propagation pass over the ``connected_to`` adjacency for
cascading delay. Deterministic end-to-end (no RNG, no clock, no I/O) and
honestly labeled ``deterministic-rules-graph-propagation`` — the trained
gradient-boosted §16.3 model remains a future artifact implementing the same
TRD §17 interface.

Semantics (documented [ASSUMPTION] coefficients, see configuration.py):
- the possession impact at the blocked section is
  ``historical_delay × base_direct_factor``;
- direct: a train routed through the blocked section receives that impact,
  attenuated by priority protection;
- cascading: the train's route is reached from the blocked section after
  ``hops`` adjacency edges; the impact decays by ``propagation_factor``
  per hop (strictly smaller than the direct impact, since factor < 1)
  and the same priority protection applies;
- unaffected: 0.0 minutes, reported explicitly.
"""

from typing import Dict, List, Tuple

from engine.delay.configuration import DelayModelConfig
from engine.delay.inputs import DelayFeatures
from engine.delay.result import (
    CLASS_CASCADING,
    CLASS_DIRECT,
    CLASS_UNAFFECTED,
    DelayPredictionResult,
    TrainDelayRecord,
)


def _protection_factor(priority: float, config: DelayModelConfig) -> float:
    """Priority protection multiplier (higher-priority trains are protected
    more strongly by dispatcher re-sequencing). Deterministic in [0, 1]."""
    scale = config.priority_scale
    normalized = min(priority / scale, 1.0)
    return 1.0 - config.priority_attenuation * normalized


def _downstream_hops(
    section_id: str,
    train_route: List[str],
    adjacency: Dict[str, List[str]],
    max_depth: int,
) -> int:
    """Minimum adjacency hops from ``section_id`` to any section on the
    train's route, or -1 when unreachable. Breadth-first, deterministic
    (adjacency lists are iterated in insertion order)."""
    route_set = set(train_route)
    if section_id in route_set:
        return 0
    frontier = [section_id]
    visited = {section_id}
    for hops in range(1, max_depth + 1):
        next_frontier: List[str] = []
        for node in frontier:
            for neighbor in adjacency.get(node, ()):
                if neighbor in visited:
                    continue
                if neighbor in route_set:
                    return hops
                visited.add(neighbor)
                next_frontier.append(neighbor)
        frontier = next_frontier
        if not frontier:
            break
    return -1


class GraphPropagationDelayModel:
    """TRD §17 model-interface implementation for the §16.3 baseline."""

    def __init__(self, config: DelayModelConfig = None):
        self._config = config or DelayModelConfig()

    @property
    def config(self) -> DelayModelConfig:
        return self._config

    def get_version(self) -> str:
        return self._config.model_dump_json()

    def predict(self, features: DelayFeatures) -> DelayPredictionResult:
        return self._compute(features)

    def predict_with_uncertainty(self, features: DelayFeatures) -> DelayPredictionResult:
        """§16.3 defines no uncertainty output for the baseline; the method
        exists to satisfy the TRD §17 interface and returns the deterministic
        result unchanged (honest: no fabricated intervals)."""
        return self._compute(features)

    def explain(self, features: DelayFeatures) -> Dict:
        return self._compute(features).explain()

    # --- internals ---------------------------------------------------------

    def _compute(self, features: DelayFeatures) -> DelayPredictionResult:
        config = self._config
        records: List[TrainDelayRecord] = []
        source_delay = features.historical_delay_minutes

        for train in features.affected_trains:
            hops = _downstream_hops(
                features.section_id,
                train.route,
                features.adjacency,
                config.max_propagation_depth,
            )
            if hops < 0:
                records.append(
                    TrainDelayRecord(
                        train_id=train.train_id,
                        classification=CLASS_UNAFFECTED,
                        delay_minutes=0.0,
                        propagation_hops=0,
                        priority_protection_factor=1.0,
                    )
                )
                continue

            classification = CLASS_DIRECT if hops == 0 else CLASS_CASCADING
            impact = source_delay * config.base_direct_factor
            decayed = impact * (config.propagation_factor**hops)
            protection = _protection_factor(train.priority, config)
            delay = decayed * protection

            records.append(
                TrainDelayRecord(
                    train_id=train.train_id,
                    classification=classification,
                    delay_minutes=delay,
                    propagation_hops=hops,
                    priority_protection_factor=protection,
                )
            )

        # Deterministic record order: classification (direct first), then
        # train_id — never input order (stable under caller reordering).
        records.sort(key=lambda r: (r.classification != CLASS_DIRECT, r.train_id))

        total = sum(r.delay_minutes for r in records)
        return DelayPredictionResult(
            window_id=features.window_id,
            section_id=features.section_id,
            trains=records,
            total_delay_minutes=total,
            confidence=config.baseline_confidence,
        )


__all__ = [
    "GraphPropagationDelayModel",
    "DelayModelConfig",
    "DelayFeatures",
    "AffectedTrain",
    "DelayPredictionResult",
    "TrainDelayRecord",
    "CLASS_DIRECT",
    "CLASS_CASCADING",
    "CLASS_UNAFFECTED",
    "DELAY_ALGORITHM",
]
