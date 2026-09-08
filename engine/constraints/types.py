"""Explicit hard/soft distinction for constraints (never numeric weights)."""

from enum import Enum


class ConstraintType(str, Enum):
    """Constraint category.

    HARD  — must never be violated; a FAIL makes the candidate infeasible
            (PRD §27, TRD §20).
    SOFT  — operational preference; may be violated at a measurable cost and
            only ever produces PASS/WARNING (TRD §20, E01 §17).
    """

    HARD = "HARD"
    SOFT = "SOFT"
