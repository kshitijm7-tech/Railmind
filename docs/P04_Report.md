# P04 — API Contracts & Service Boundaries

## Objective
Establish the canonical API transportation layer (`frontend/contracts/api/`) across the RailMind platform. This introduces structured requests, responses, querying rules, and HTTP endpoint truth, keeping the domain boundary cleanly separated from infrastructure constraints.

## Endpoint Families
Over 30 distinct API endpoints were established covering all domains:
- **System**: Health, API version checking
- **Infrastructure**: Network sections, station assets
- **Maintenance**: Task scheduling, defect reporting
- **Operations**: Train operations, window tracking
- **Planning**: Block generation, constraints, plan analysis
- **Simulation**: Scenario simulation runs, results
- **Disruption**: Disruption mapping, incident impact
- **Recovery**: Recovery scenarios, replan triggers
- **Decision**: Recommendation histories, approvals
- **Audit**: Log event histories

## Core Common Contracts Established
- **`ApiResponse<T>` / `ApiListResponse<T>`**: Standard response envelopes encapsulating meta details.
- **`PaginationMeta` / `SortParams` / `DateRangeFilter`**: Shared metadata querying interfaces.
- **`ApiError` / `ApiErrorResponse`**: Clean error mapping bound to domain error codes.
- **`ScenarioContext`**: Safety boundary mechanism enforcing that live operational state cannot be accidentally mutated during scenarios.

## Architectural Additions
- **Async Job Strategy**: `job.ts` defines `AsyncJob` and `JobAcceptedResponse`. Any potentially heavy backend task (planning generation, simulation runs) is structured as a `202 Accepted` queue operation with subsequent polling.
- **Unified Endpoints Source of Truth**: All URL paths are consolidated in `endpoints.ts`.

## Service Refactoring
The frontend integration layer `services/types.ts` and `mockServices.ts` were upgraded:
1. Replaced generic querying signatures with strictly typed queries (e.g., `MaintenanceTaskListQuery`).
2. Updated heavy methods like `generatePlan()` and `runSimulation()` to return `AsyncJob` entities instead of immediate mock plan fulfillment.
3. Aligned API operations directly with the domain.

## Validation Results
- **Typecheck**: `PASS`
- **Lint**: `PASS`
- **Vitest**: `PASS` (39 tests passed)
- **Next Build**: `PASS`

## Deferred Work
Auth placeholder strings exist in `RequestContext` to be formally fleshed out alongside User models.

## Recommendation for P05
Implement the actual FastAPI backend mapping to these precise openapi/contract specs, utilizing Python equivalents.
