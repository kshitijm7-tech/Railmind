"""Planner errors (E09) — loud failure at the solver boundary.

Follows the E01–E08 convention: invalid engine-contract states are raised,
never silently repaired or defaulted.
"""


class PlannerError(ValueError):
    """Raised when the planner cannot produce a valid plan.

    Covers: solver returning no solution inside the configured budget,
    structurally infeasible instances, and extractor/evaluation contract
    violations. Callers (backend adapter) map this to the established
    400-series domain error taxonomy.
    """


__all__ = ["PlannerError"]
