# P07 Block Planning Backend Implementation Report

## Summary
The P07 implementation successfully establishes the deterministic block planning engine for RailMind. The backend consumes the infrastructure, maintenance, and operations data established in P06 to generate conflict-free `CandidateBlockWindow` instances and construct `Plan` versions. 

## Key Additions & Modifications
1. **TS Contracts Alignment**:
   - Updated Python models in `backend/app/domain/models/planning.py` to perfectly match `frontend/contracts/planning/` schemas (e.g. `CandidateBlockWindow`, `Block`, `Plan`, `PlanMetrics`, `PlanVersion`).
   - Extended `backend/app/api/models.py` with the asynchronous job handling models (`AsyncJob`, `JobAcceptedResponse`) and plan API requests (`GeneratePlanRequest`, `ComparePlansRequest`, etc.).
   - Replaced old Enums in `backend/app/domain/enums.py` with TS-accurate string definitions (e.g., `PlanStrategy.MAINTENANCE_MAXIMIZED`, `PlanStatus.ARCHIVED`, `BlockStatus`).

2. **Domain Logic (Deterministic Planning)**:
   - Built `CandidateGenerator` that iterates over `OperationalWindow` instances to evaluate sufficient duration against a `MaintenanceTask`.
   - Built `ConflictDetector` that computes simple time-range overlaps against segments of `TrainPath` allocations.

3. **Application Services**:
   - Updated `PlanningService` to accept repositories for infrastructure, operations, and maintenance.
   - Designed `generate_plan(request)`: 
     - Retrieves tasks and ops constraints.
     - Iteratively builds candidates, assesses conflicts, and chooses deterministically.
     - Saves the constructed plan to `InMemoryPlanRepository`.
     - Returns a `202 Accepted` response with an `AsyncJob` mimicking a long-running execution.
   - Built `compare_plans(plan_ids)` to evaluate user-specified plans across constraint violations and metrics.

4. **API Integration**:
   - Implemented `backend/app/api/v1/endpoints/planning.py`.
   - Wired endpoints: `/plans`, `/plans/{id}`, `/plans/{id}/versions`, `/plans/{id}/metrics`, `/planning/candidates`, `/planning/blocks`, `/planning/generate`, and `/plans/compare`.

5. **Testing & Stability**:
   - Tests were appended to `backend/tests/test_api.py` validating 202 status code and deterministic job assignments.
   - All backend `pytest` unit tests passed successfully.
   - All frontend typescript checks, linting, tests, and build completed successfully.

## Next Steps
In the subsequent phase, we will introduce CP-SAT integration or integrate this mock logic into a full database-backed persistent storage, unlocking robust scenario evaluation.
