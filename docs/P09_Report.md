# P09: Constraint & Rules Engine Implementation

## Overview
This report summarizes the implementation of the Constraint & Rules Engine (P09) for RailMind. The goal of this phase was to build a deterministic rule engine capable of evaluating maintenance candidate block windows with precise, explainable rules without using complex CP-SAT solvers. 

## Architectural Additions
1. **Engine Submodule (`app.domain.engine`)**:
   - `models.py`: Defines core data structures like `ConstraintSeverity` (HARD/SOFT), `ConstraintStatus` (FEASIBLE, INFEASIBLE, FEASIBLE_WITH_WARNINGS), `ConstraintViolation` with `evidence` fields, and `EvaluationContext`.
   - `rules.py`: Implements deterministic rules (`OperationalWindowRule`, `MaintenanceDurationRule`, `TrainPathConflictRule`, `PreferredWindowRule`) following a cohesive `Rule` protocol. 
   - `core.py`: Encapsulates the `ConstraintEngine` responsible for registering and evaluating rules against candidate blocks, merging all violations, and deriving the overall `ConstraintStatus`.
   
2. **Integration (`app.domain.logic.planning` & `app.application.services.planning_service`)**:
   - Replaced hardcoded string-based conflicts in `ConflictDetector` with a unified evaluation call to `ConstraintEngine`.
   - Expanded `CandidateBlockWindow` schema with a new `violations` array containing the rich evaluation objects (`ConstraintViolation`) so that consuming systems can provide clear evidence, while maintaining the legacy `conflicts` array for backward compatibility.
   
3. **API (`app.api.v1.endpoints.engine`)**:
   - Exposed `POST /api/v1/engine/constraints/evaluate` endpoint to test candidates ad-hoc.
   - Connected `engine.router` in `router.py`.

## Tested Behaviors
A comprehensive test suite was written (`backend/tests/test_engine.py`) to cover:
- Exact fit boundary conditions for operational windows.
- Maintenance durations shorter than the expected duration triggering hard violations.
- Precise overlap detection for train path conflicts on shared track sections.
- Adjacency tests (where candidate blocks share boundaries with train paths but don't strictly overlap) passing without violation.
- Soft constraint evaluation via the preferred window rule, appropriately flagging nighttime-aligned tasks versus daytime schedules.

All tests passed successfully, validating the engine's capability for robust, explainable rule evaluation. Frontend contracts remain intact.
