"""PriorityEngine (E02) — deterministic, explainable, configurable.

Computes the maintenance priority of one task as a weighted mean of
normalized factor scores:

    score = Σ (normalized_factor_i × normalized_weight_i)

Weights come from ``PriorityEngineConfig`` (PRD FR-MI-001 defaults
0.30/0.20/0.20/0.20/0.10). The engine never mutates configuration and never
uses clocks or randomness: identical inputs always produce identical results.
"""

from typing import Dict, List, Optional, Tuple

from engine._version import CONSTRAINT_SET_ID, CONSTRAINT_SET_VERSION
from engine.priority.configuration import PriorityEngineConfig
from engine.priority.factors import (
    FactorOutcome,
    criticality_factor,
    downstream_impact_factor,
    failure_risk_factor,
    overdue_factor,
    safety_factor,
)
from engine.priority.inputs import PriorityInput
from engine.priority.missing_data import MissingDataPolicy
from engine.priority.result import FactorScore, PriorityResult

#: factor name → config weight attribute (deterministic iteration order)
_FACTOR_WEIGHT_KEYS: Tuple[Tuple[str, str], ...] = (
    ("criticality", "criticality_weight"),
    ("overdue", "overdue_weight"),
    ("failure_risk", "failure_risk_weight"),
    ("safety", "safety_weight"),
    ("downstream_impact", "downstream_impact_weight"),
)


def classify(score: float, config: PriorityEngineConfig) -> str:
    """Threshold classification onto the canonical enum (LOW|MEDIUM|HIGH|CRITICAL).

    Boundary ownership is explicit: a score exactly on a threshold belongs to
    the higher class (>= semantics).
    """
    if score >= config.threshold_critical:
        return "CRITICAL"
    if score >= config.threshold_high:
        return "HIGH"
    if score >= config.threshold_medium:
        return "MEDIUM"
    return "LOW"


class PriorityEngine:
    def __init__(self, config: Optional[PriorityEngineConfig] = None):
        # Boundary validation: an all-zero weight configuration cannot
        # produce a meaningful priority and is rejected here (normalized
        # weights raise) — never a misleading score.
        self._config = config or PriorityEngineConfig()
        self._config.normalized_weights()  # validation probe

    @property
    def config(self) -> PriorityEngineConfig:
        return self._config

    def evaluate(self, task: PriorityInput) -> PriorityResult:
        cfg = self._config
        policy = cfg.missing_data_policy

        outcomes: List[FactorOutcome] = [
            criticality_factor(task.criticality, cfg),
            overdue_factor(task.overdue_days, cfg),
            failure_risk_factor(task, cfg),
            safety_factor(task, cfg),
            downstream_impact_factor(task, cfg),
        ]
        present = [o for o in outcomes if o.present]
        missing = [o for o in outcomes if not o.present]

        if policy is MissingDataPolicy.ZERO:
            # Absent factors score 0.0 and keep their full weight.
            effective = outcomes
            weights: Dict[str, float] = cfg.normalized_weights()
        else:
            # EXCLUDE_FACTOR (default): renormalise weights across present
            # factors so the score stays a true weighted mean of what is
            # known; every exclusion is reported, never silent.
            present_names = {o.factor for o in present}
            weight_map = {
                name: getattr(cfg, key)
                for name, key in _FACTOR_WEIGHT_KEYS
                if name in present_names
            }
            total = sum(weight_map.values())
            if total <= 0.0:
                raise ValueError(
                    "all supplied factors carry zero weight; cannot compute a "
                    "meaningful priority (check weight configuration and "
                    "missing-data policy)"
                )
            weights = {name: w / total for name, w in weight_map.items()}
            effective = present

        factor_scores: List[FactorScore] = []
        weighted_sum = 0.0
        weight_total = 0.0
        for outcome in effective:
            weight = weights[outcome.factor]
            contribution = outcome.normalized_score * weight
            weighted_sum += contribution
            weight_total += weight
            factor_scores.append(
                FactorScore(
                    factor=outcome.factor,
                    raw_value=outcome.raw_value,
                    raw_description=outcome.raw_description,
                    normalized_score=outcome.normalized_score,
                    weight=weight,
                    contribution=contribution,
                    source=outcome.source,
                )
            )

        # Final guard: the score is the weighted mean of the normalized
        # scores (Σ weights == 1.0 up to float tolerance).
        score = weighted_sum / weight_total if weight_total > 0.0 else 0.0

        priority_class = classify(score, cfg)
        return PriorityResult(
            task_id=task.task_id,
            score=score,
            priority_class=priority_class,
            factor_scores=factor_scores,
            missing_factors=[o.factor for o in missing]
            if policy is MissingDataPolicy.EXCLUDE_FACTOR
            else [],
            missing_data_policy=policy.value,
            explanation=_build_explanation(task, score, priority_class, factor_scores, missing, policy),
            evidence=_build_evidence(factor_scores, missing),
            metadata={
                "section_id": task.section_id,
                "asset_id": task.asset_id,
                "weights_renormalized": abs(cfg.weights_sum() - 1.0) > 1e-9,
                "constraint_set_id": CONSTRAINT_SET_ID,
                "constraint_set_version": CONSTRAINT_SET_VERSION,
            },
        )


def _fmt(value: float) -> str:
    """Stable two-decimal formatting for user-facing explanations."""
    return f"{value:.2f}"


def _build_explanation(
    task: PriorityInput,
    score: float,
    priority_class: str,
    factor_scores: List[FactorScore],
    missing: List[FactorOutcome],
    policy: MissingDataPolicy,
) -> str:
    contributors = sorted(
        (f for f in factor_scores if f.contributed),
        key=lambda f: (-f.contribution, f.factor),
    )
    lines = [
        (
            f"Task {task.task_id} classified {priority_class} with priority "
            f"score {_fmt(score)} — driven by: "
        )
    ]
    if contributors:
        lines.append(
            "; ".join(
                f"{f.factor} ({f.raw_description}, normalized {_fmt(f.normalized_score)}, "
                f"weight {_fmt(f.weight)}, contribution {_fmt(f.contribution)})"
                for f in contributors
            )
        )
    else:
        lines.append("no factor contributed above zero")
    zero_weight = [f.factor for f in factor_scores if f.weight == 0.0]
    if zero_weight:
        lines.append(f"Zero-weight factors: {', '.join(zero_weight)}.")
    if missing:
        if policy is MissingDataPolicy.EXCLUDE_FACTOR:
            lines.append(
                f"Missing optional factor(s) {', '.join(o.factor for o in missing)} "
                f"excluded under {policy.value} (weights renormalised)."
            )
        else:
            lines.append(
                f"Absent optional factor(s) {', '.join(o.factor for o in missing)} "
                f"scored 0.0 with retained weight ({policy.value})."
            )
    return "\n".join(lines)


def _build_evidence(
    factor_scores: List[FactorScore],
    missing: List[FactorOutcome],
) -> List[str]:
    items = [
        f"{f.factor}: {f.raw_description} → normalized {_fmt(f.normalized_score)}"
        for f in factor_scores
    ]
    items.extend(f"missing:{o.factor} ({o.missing_reason})" for o in missing)
    return items
