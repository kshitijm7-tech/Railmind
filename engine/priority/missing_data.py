"""Missing-data policy for optional priority factors (E02).

The PRD defines ``overdue_days: int  # 0 if not overdue`` (§11.2) — never
unknown — so overdue days is a REQUIRED factor and its absence is a
construction error. The remaining optional factors (asset failure risk,
safety relevance, downstream train impact) have no canonical
"unknown" representation, and fabricating one would violate the
no-invented-data discipline.

Policy (deliberate, explicit, deterministic):

- ``EXCLUDE_FACTOR`` — the factor is omitted from the weighted score and its
  weight is renormalised across the present factors, so the score stays a
  true weighted mean of what is known. Every exclusion is reported in the
  result (``missing_factors`` + evidence), never silent.
- ``ZERO``           — the factor scores 0.0 (neutral/absent) and keeps its
  full weight. Transparent, but drags the score down for missing data.

The default is ``EXCLUDE_FACTOR``. Safety-critical handling: criticality is
REQUIRED and fails closed at the model boundary (no neutral default exists
for an unknown criticality).
"""

from enum import Enum


class MissingDataPolicy(str, Enum):
    EXCLUDE_FACTOR = "EXCLUDE_FACTOR"
    ZERO = "ZERO"
