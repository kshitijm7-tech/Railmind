"""Factor normalization (E02).

Each factor maps its raw input onto a bounded [0, 1] score using the
configuration's explicit mappings/saturation points — no magic numbers, no
hidden interpretation. Normalization is deterministic and monotonic by design
(higher raw input ⇒ score ≥ lower raw input for the same configuration).
"""

from dataclasses import dataclass
from typing import Optional

from engine.priority.configuration import PriorityEngineConfig
from engine.priority.inputs import PriorityInput


@dataclass(frozen=True)
class FactorOutcome:
    """Raw value + normalized score for one factor."""

    factor: str
    raw_value: Optional[float]
    raw_description: str
    normalized_score: float
    source: str
    present: bool = True
    missing_reason: str = ""


def _normalize_bounded(value: float, saturation: float) -> float:
    """Linear normalization onto [0, 1]: value/saturation, capped at 1.0."""
    if saturation <= 0:
        raise ValueError("saturation bound must be positive")
    return min(value / saturation, 1.0)


def criticality_factor(
    criticality: str, config: PriorityEngineConfig
) -> FactorOutcome:
    """Canonical enum → explicit score mapping (LOW .25 / MEDIUM .50 / HIGH .75 / CRITICAL 1.0)."""
    scores = config.criticality_scores
    if criticality not in scores:
        # Configuration error, not a data gap: the mapping must cover the
        # canonical enum. Fail loudly at evaluation time.
        raise ValueError(
            f"criticality_scores config lacks an entry for {criticality!r}"
        )
    return FactorOutcome(
        factor="criticality",
        raw_value=None,  # categorical: the enum itself is the raw value
        raw_description=f"criticality={criticality}",
        normalized_score=float(scores[criticality]),
        source="canonical:Criticality",
    )


def overdue_factor(overdue_days: int, config: PriorityEngineConfig) -> FactorOutcome:
    """Linear saturation normalization: 0 days → 0.0, saturation → 1.0."""
    normalized = _normalize_bounded(float(overdue_days), config.overdue_saturation_days)
    return FactorOutcome(
        factor="overdue",
        raw_value=float(overdue_days),
        raw_description=f"{overdue_days} day(s) overdue (saturation {config.overdue_saturation_days:.0f}d)",
        normalized_score=normalized,
        source="canonical:overdue_days",
    )


def failure_risk_factor(
    task: PriorityInput, config: PriorityEngineConfig
) -> FactorOutcome:
    """Asset failure risk: the probability itself is the bounded score."""
    risk = task.asset_failure_risk
    if risk is None:
        return FactorOutcome(
            factor="failure_risk",
            raw_value=None,
            raw_description="no asset failure-risk data supplied",
            normalized_score=0.0,
            source="",
            present=False,
            missing_reason="asset_failure_risk not provided",
        )
    return FactorOutcome(
        factor="failure_risk",
        raw_value=risk.probability_of_failure,
        raw_description=(
            f"P(failure)={risk.probability_of_failure:.2f} over "
            f"{risk.time_horizon_hours:.0f}h"
        ),
        normalized_score=risk.probability_of_failure,
        source=risk.source,
    )


def safety_factor(task: PriorityInput, config: PriorityEngineConfig) -> FactorOutcome:
    """Safety relevance: explicit flag dominates; otherwise task-type mapping.

    With an explicit flag: score = safety_flag_score (1.0 when set, 0.0 when
    explicitly not safety-relevant). Without one: the task-type map provides a
    prior (EMERGENCY 1.0 / CORRECTIVE 0.75 / INSPECTION 0.25 / PREVENTIVE 0.0)
    scaled by ``safety_task_type_weight_share`` — the residual share stays at
    the neutral 0.0 so the factor never overstates what is known. An
    explicitly non-safety flag is stronger evidence than a task-type prior
    and therefore forces the score to 0.0.
    """
    if task.is_safety_relevant is True:
        return FactorOutcome(
            factor="safety",
            raw_value=1.0,
            raw_description="explicit safety-relevant flag",
            normalized_score=config.safety_flag_score,
            source="input:is_safety_relevant",
        )
    if task.is_safety_relevant is False:
        return FactorOutcome(
            factor="safety",
            raw_value=0.0,
            raw_description="explicitly not safety-relevant",
            normalized_score=0.0,
            source="input:is_safety_relevant",
        )
    if task.task_type is not None:
        prior = config.safety_task_type_scores.get(task.task_type)
        if prior is None:
            raise ValueError(
                f"safety_task_type_scores config lacks an entry for {task.task_type!r}"
            )
        score = prior * config.safety_task_type_weight_share
        return FactorOutcome(
            factor="safety",
            raw_value=prior,
            raw_description=(
                f"task_type={task.task_type} prior {prior:.2f} "
                f"× share {config.safety_task_type_weight_share:.2f}"
            ),
            normalized_score=score,
            source="config:safety_task_type_scores",
        )
    return FactorOutcome(
        factor="safety",
        raw_value=None,
        raw_description="no safety flag and no task type supplied",
        normalized_score=0.0,
        source="",
        present=False,
        missing_reason="neither is_safety_relevant nor task_type provided",
    )


def downstream_impact_factor(
    task: PriorityInput, config: PriorityEngineConfig
) -> FactorOutcome:
    """Downstream operational impact: trains/day on the section, saturated."""
    if task.trains_per_day is None:
        return FactorOutcome(
            factor="downstream_impact",
            raw_value=None,
            raw_description="no section traffic volume supplied",
            normalized_score=0.0,
            source="",
            present=False,
            missing_reason="trains_per_day not provided",
        )
    normalized = _normalize_bounded(task.trains_per_day, config.downstream_trains_per_day_saturation)
    return FactorOutcome(
        factor="downstream_impact",
        raw_value=task.trains_per_day,
        raw_description=(
            f"{task.trains_per_day:.0f} trains/day "
            f"(saturation {config.downstream_trains_per_day_saturation:.0f})"
        ),
        normalized_score=normalized,
        source="input:trains_per_day",
    )
