"""Priority result model (E02) — explainable by construction.

Every factor that influenced the score is exposed with its raw value,
normalization outcome, weight and contribution; the score is reproducible
from the factor list alone.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict

from engine._version import ENGINE_VERSION, PRIORITY_MODEL_ID, PRIORITY_MODEL_VERSION


class FactorScore(BaseModel):
    """One weighted factor's contribution to the priority score."""

    model_config = ConfigDict(frozen=True)

    factor: str
    raw_value: Optional[float] = None
    raw_description: str = ""
    normalized_score: float  # always in [0, 1]
    weight: float  # normalized weight (all exposed weights sum to 1.0)
    contribution: float  # normalized_score × weight
    source: str = ""  # where the raw value came from (canonical field / model)

    @property
    def contributed(self) -> bool:
        return self.weight > 0.0 and self.normalized_score > 0.0


class PriorityResult(BaseModel):
    """Explainable priority verdict for one maintenance requirement.

    Invariants (tested):
    - ``score`` == Σ factor contributions (within float tolerance);
    - Σ exposed factor weights == 1.0 (weights are renormalised when the
      configuration does not sum to 1, or when factors are excluded);
    - identical inputs + configuration → byte-identical result.
    """

    model_config = ConfigDict(frozen=False)

    task_id: str
    score: float  # [0, 1]
    priority_class: str  # LOW | MEDIUM | HIGH | CRITICAL (canonical enum)

    factor_scores: List[FactorScore] = []
    missing_factors: List[str] = []  # optional factors absent under EXCLUDE policy
    missing_data_policy: str = ""

    explanation: str = ""
    evidence: List[str] = []
    metadata: Dict[str, Any] = {}

    engine_version: str = ENGINE_VERSION
    priority_model_id: str = PRIORITY_MODEL_ID
    priority_model_version: str = PRIORITY_MODEL_VERSION

    @property
    def weight_total(self) -> float:
        return sum(f.weight for f in self.factor_scores)

    @property
    def contribution_total(self) -> float:
        return sum(f.contribution for f in self.factor_scores)

    def contributing_factors(self) -> List[FactorScore]:
        """Factors ordered by contribution (descending), deterministic tie-break."""
        return sorted(
            (f for f in self.factor_scores if f.contributed),
            key=lambda f: (-f.contribution, f.factor),
        )
