# RailMind OpenCode Onboarding Report

## 1. Git State

- **Current branch**: `opencode/frontend`
- **Remote**: `origin` (GitHub: https://github.com/kshitijm7-tech/Railmind)
- **Available relevant branches**:
  - `antigravity/core` — primary backend/architecture branch
  - `freebuff/engine` — intelligence/optimization branch
  - `main` — default production branch
  - `opencode/frontend` — the required working branch (currently checked out)
- **Synchronization**: Local `opencode/frontend` is up to date with `origin/opencode/frontend` (no diverging commits)
- **Verification**: `git branch --show-current` returns `opencode/frontend`

---

## 2. Repository Structure

The repository is a monorepo-style setup with a Next.js 16 frontend:

```
Frontend/ (D:\Projects\Railmind\frontend)
├── app/              — Next.js pages (audit, decisions, disruptions,
                      maintenance, operations, planning, simulation,
                      settings, trains)
├── components/       — Reusable UI organized by domain:
│   ├── layout/       — AppShell, Sidebar, TopBar, GlobalContextBar,
│   │                 ScenarioBanner, GlobalSearchModal
│   ├── operational/  — DataTable, MetricCard, EvidenceViews
│   ├── decision/     — DecisionCard (human-in-the-loop workflow)
│   ├── railway/      — DepartmentBadge, CriticalityBadge, TrainBadge,
│   │                 SectionBadge
│   ├── state/        — StateBadge (LIVE/ACTUAL/PREDICTION/SCENARIO)
│   ├── ui/           — Button component
│   └── feedback/     — LoadingState, EmptyState, ErrorState, ComputeState
├── contracts/        — **Canonical API contracts** (source of truth):
│   ├── api/          — Typed requests/responses per domain:
│   │   ├── maintenance, operations, planning, simulation,
│   │   ├── decision, audit, common
│   │   └── envelope (ApiResponse, ApiListResponse, ScenarioContext,
│   │           RequestContext, ApiMeta, PaginationParams, etc.)
│   ├── ai/           — PredictionBase, PriorityPrediction, DurationPrediction,
│   │               DelayPrediction, FailureRiskPrediction
│   ├── common/       — Branded IDs (ids.ts), Enums (enums.ts), Errors (errors.ts),
│   │               Provenance (provenance.ts), Time (time.ts)
│   ├── decision/, disruption/, events/, infrastructure/, maintenance/,
│   ├── planning/, simulation/ — Domain-specific contracts
│   └── index.ts — Re-exports all contract modules
├── context/          — React context providers:
│   └── OperationalContext.tsx — Manages LIVE vs SCENARIO mode,
                                metadata, active scenario, refreshState
├── domain/           — Domain types network, maintenance, trains,
                      blocks, plans, recommendations, simulation,
                      disruptions, decisions, search
├── fixtures/         — Demo data (demoCorridor.ts) for mock services
├── services/         — Service layer implementing API interfaces:
│   ├── api/          — MockNetworkService, MockMaintenanceService, etc.
│   │   (all 10 services: network, maintenance, trains, planning,
│   │   simulation, disruption, recommendations, decisions, audit, search)
│   ├── mock/         — MockService implementations using fixtures
│   └── types.ts      — Service interface definitions (INetworkService, etc.)
├── tests/            — 9 Vitest test files, 39 tests all passing:
│   ├── mock-services.test.ts     (5 tests)
│   ├── api-contracts.test.ts     (17 tests)
│   ├── contracts-validation.test.ts (4 tests)
│   ├── data-table.test.tsx       (2 tests)
│   ├── decision-card.test.tsx    (2 tests)
│   ├── state-badges.test.tsx     (4 tests)
│   ├── search-context.test.tsx   (2 tests)
│   ├── global-context.test.tsx   (1 test)
│   └── app-shell.test.tsx        (2 tests)
├── config/           — workspaceConfig.ts (page title/eyebrow config)
└── package.json      — Next.js 16, React 19, TypeScript 5.9,
                        vitest for testing, eslint for linting
```

**Key Observations**:
- Frontend is **Next.js 16** with React 19 and TypeScript 5.9
- All testing, linting, and typechecking pass
- Mock data is cleanly separated behind the service layer
- Live vs Scenario state distinction is implemented at the context level
- Contracts-first architecture — frontend types import from `contracts/`, never redefine

---

## 3. Context Reviewed

The following context documents and directories were inspected:

- `context/OperationalContext.tsx` — Operational context provider managing `mode: 'LIVE' | 'SCENARIO'` state, metadata, active scenario, and `refreshState` (fetches from `services.network.getStateMetadata()`)
- `P00_Report.md` through `P08_Report.md` — Project history confirming phases P00-P08 are complete
- `config/workspaceConfig.ts` — Page title/eyebrow configuration per route
- `fixtures/demoCorridor.ts` — Comprehensive demo data (network, maintenance tasks, trains, plans, recommendations, incidents, scenarios, audit events) used by mock services

**No separate PRD, TRD, or UI/UX specification documents were found beyond the agent rules and phase reports already captured in P00-P08.**

---

## 4. Architecture Understanding

The frontend follows a **service layer pattern** with clean API boundaries:

```
UI
 ↓
Feature/Application Layer (pages/components)
 ↓
Frontend Service Layer (services/)
 ↓
API Client (services types → contracts/api requests)
 ↓
FastAPI
```

**Key architectural elements**:

- **OperationalContextProvider** (`context/OperationalContext.tsx`) — Core state manager that distinguishes `LIVE` operational mode from `SCENARIO` simulation mode. When a scenario is entered, metadata mode switches to `'SCENARIO'` and `activeScenarioId/Name` are set. Exit resets to `'LIVE'`.

- **ServiceContainer** (`services/index.ts`) — Injects all 10 services (network, maintenance, trains, planning, simulation, disruption, recommendations, decisions, audit, search). Currently uses mock implementations, but the interface is typed and ready for real implementations.

- **ScenarioContext** (`contracts/api/common/envelope.ts`) — SAFETY BOUNDARY: every API request carries `scenarioContext: { mode: StateMode; scenarioId?: ScenarioId }`. This ensures scenario state never silently mutates live state.

- **Branded ID types** (`contracts/common/ids.ts`) — Prevents accidental ID cross-assignment (TrainId, AssetId, BlockId, etc. are distinct branded types).

- **Provenance tracking** (`contracts/common/provenance.ts`) — Every data entity carries `source: DataState` (REAL/MOCKED/SIMULATED/STUBBED/PLANNED) and `source: DataSource` (BDMS/TMS/SMMS/TDMS/COA/USER/AI/SIMULATION/SYNTHETIC/IMPORT/SYSTEM).

- **AsyncJob pattern** (`contracts/api/common/job.ts`) — Plan generation and simulation return `202 Accepted` with a `pollEndpoint` for long-running operations.

- **Human-in-the-loop** — DecisionCard explicitly requires `onApprove/onReject/onModify` callbacks. Never auto-executes. Workflow: Recommendation → Evidence → Impact → Human Review → Approve/Reject/Defer.

---

## 5. Backend/API Understanding

The frontend API surface is fully defined through typed contracts. Only the integration layer needs to connect to the real backend:

**Service Interfaces** (`services/types.ts`):

| Service | Key Methods |
|---------|-------------|
| `INetworkService` | `getNetwork()`, `getStateMetadata()` |
| `IMaintenanceService` | `getTasks()`, `getTaskById()`, `createTask()`, `getDefects()` |
| `ITrainService` | `getTrains()`, `getTrainById()` |
| `IPlanningService` | `getCandidateWindows()`, `getPlans()`, `getPlanById()`, `generatePlan()`, `comparePlans()` |
| `ISimulationService` | `getScenarios()`, `runSimulation()`, `getSimulationResult()` |
| `IDisruptionService` | `getActiveIncidents()`, `getIncidentById()`, `createDisruption()` |
| `IRecommendationService` | `getLatestRecommendation()`, `getRecommendationById()` |
| `IDecisionService` | `getDecisionHistory()`, `approveDecision()`, `rejectDecision()`, `deferDecision()` |
| `IAuditService` | `getAuditEvents()` |
| `ISearchService` | `search()` |

**Key API Patterns**:

- All list queries support `PaginationParams`, `SortParams`, `DateRangeFilter`, and `ScenarioContext`
- `GeneratePlanRequest` includes `horizon`, `corridorId`, `strategy`, optional `taskIds`, `objectiveWeights`, `scenarioContext`, and `idempotencyKey`
- `RunSimulationRequest` requires `planId`, `scenarioId`, `scenarioContext`, optional `assumptions`, and `idempotencyKey`
- `ApproveDecisionBody`, `RejectDecisionBody`, `DeferDecisionBody` include `approver`, `role`, and `justification/reason`
- All mutation operations support idempotency keys to prevent duplicate operations

**API Contract Organization** (`contracts/api/`):

- `common/` — Envelope types (ApiResponse, ApiListResponse, ScenarioContext, RequestContext, ApiMeta, PaginationParams, SortParams, DateRangeFilter, IdempotencyHeader)
- `maintenance/` — MaintenanceTaskListQuery, CreateMaintenanceTaskBody, DefectListQuery, CreateDefectBody
- `operations/` — TrainListQuery, TrainPathListQuery, OperationalWindowListQuery, TrainImpactListQuery
- `planning/` — BlockListQuery, BlockRequestBody, GeneratePlanRequest, PlanListQuery, ComparePlansRequest
- `simulation/` — RunSimulationRequest, SimulationListQuery
- `decision/` — RecommendationListQuery, DecisionListQuery, ApproveDecisionBody, RejectDecisionBody, DeferDecisionBody
- `audit/` — AuditEventListQuery

All requests/responses are fully typed, and the `envelope` layer provides consistent `requestId`, `timestamp`, `apiVersion` (`v1`), and `correlationId` on every response.

---

## 6. Contract Understanding

**Contracts live in `frontend/contracts/` — this is the canonical source of truth.**

The frontend never independently redefines domain models. Instead:

- `domain/types/` — Thin re-exports or narrow types from contracts for UI consumption
- `services/` — Implements the service interfaces using contract types
- Components — Consume data through the service layer, not raw API calls

**Contract hierarchy**:

1. **`contracts/common/`** — Foundational types used across all domains:
   - `ids.ts` — Branded ID types (`TrainId`, `AssetId`, `BlockId`, `PlanId`, `ScenarioId`, etc.) with factory functions
   - `enums.ts` — Criticality, Department, StateMode, StateType, RiskLevel, UserRole
   - `errors.ts` — ErrorCategory, ErrorSeverity, DomainError, ERROR_CODES (RAILMIND_001 RAILMIND_020)
   - `provenance.ts` — DataSource (REAL/MOCKED/SIMULATED/STUBBED/PLANNED), DataState, Provenance interface
   - `time.ts` — TimeInterval, DurationMinutes, PlanningHorizon, ScheduledTiming

2. **Domain-specific contracts** — Each feature area has its own subdirectory:
   - `maintenance/` — Task and defect contracts
   - `planning/` — Block, Plan, CandidateBlockWindow, PlanMetrics
   - `simulation/` — Scenario, SimulationResult, SimulationRun
   - `decision/` — Recommendation, DecisionRecord
   - `disruption/` — Disruption, RecoveryPlan, RecoveryAction
   - `events/` — Command<T> envelope, EventEnvelope<T>, BlockApprovedEvent, DisruptionReportedEvent
   - `ai/` — PredictionBase, PriorityPrediction, DurationPrediction, DelayPrediction, FailureRiskPrediction

3. **`contracts/api/`** — Typed API requests/responses mapped to HTTP endpoints:
   - Request/response pairs for every endpoint
   - Consistent envelope (`ApiResponse`, `ApiListResponse`) with `requestId`, `timestamp`, `apiVersion`
   - `ScenarioContext` safety boundary on every request to distinguish LIVE vs SCENARIO

**Frontend consumption pattern** (from `services/index.ts`):

```typescript
export const services: ServiceContainer = {
  network: new MockNetworkService(),     // implements INetworkService
  maintenance: new MockMaintenanceService(), // implements IMaintenanceService
  // ... all 10 services
};
```

The service layer abstracts away the API client, and components never call `fetch` directly.

---

## 7. Existing Frontend

The frontend already has significant implementation across the roadmap phases:

**Implemented Screens/ Pages**:

- **Command Center** (`app/operations/page.tsx`) — Main operational dashboard showing:
  - Metric cards (active deficits, train paths, scheduled possessions, disruptions)
  - Priority Operational Recommendation with DecisionCard
  - Top priority maintenance backlog (DataTable)
  - Active high-priority trains
  - Live telemetry state badge

- **Decisions Workspace** (`app/decisions/`) — DecisionCard component with:
  - Structured evidence (primary rationale, expected impact, risk/robustness)
  - Alternative plan comparison
  - Human authorization workflow (Approve/Reject/Modify buttons)
  - Collapsible objective breakdown and constraint trace

- **Maintenance Workspace** (`app/maintenance/`) — Not explicitly a page but tasks are integrated into Command Center

- **Planning Workspace** (`app/planning/`) — Block windows, candidate windows, plan generation

- **Simulation Workspace** (`app/simulation/`) — Scenario creation, modification, running simulation, impact viewing

- **Audit Workspace** — Audit events browsing

- **State Management** — OperationalContext provides live/scenario mode distinction

**Reusable Components** (all tested):

- `DataTable` — Generic table with column definitions, supports custom cell renderers
- `MetricCard` — KPI display with status tone coloring (normal/attention/warning/critical)
- `DecisionCard` — Human-in-the-loop recommendation card with evidence, alternatives, approval workflow
- `StateBadge` — Visual indicator for LIVE/ACTUAL/PREDICTION/SCENARIO states with color-coded prefixes
- `DepartmentBadge` — Color-coded department tags (Engineering, S&T, TRD, OHE)
- `CriticalityBadge` — Criticality level tags (LOW/MEDIUM/HIGH/CRITICAL)
- `TrainBadge` — Train type (Passenger/Freight) and priority rank display
- `SectionBadge` — Section identifier display
- `LoadingState`, `EmptyState`, `ErrorState` — Common UI states
- `ComputeState` — CP-SAT engine status visualization
- `ScenarioBanner` — Live/scenario mode banner at top of AppShell

**Global Functionality**:

- Search provider with Ctrl+K shortcut and global search modal
- Sidebar navigation with corridor context
- Top bar with page title and eyebrow

---

## 8. Existing UI

**What can be reused**:

- **AppShell** — Complete shell layout with Sidebar, TopBar, GlobalContextBar, ScenarioBanner, GlobalSearchModal. Already supports workspace config per route.
- **StateBadge** — Properly distinguishes LIVE/ACTUAL/PREDICTION/SCENARIO modes with color coding and prefixes. Tested with all 4 states.
- **MetricCard** — KPI display with status tone support. Used in Command Center.
- **DecisionCard** — Full human-in-the-loop workflow with evidence display, alternative comparison, and Approve/Reject/Modify callbacks. Tested and working.
- **Badges** (Department, Criticality, Train, Section) — Color-coded, well-styled, accessible components.
- **DataTable** — Generic table component used in Command Center backlog view.
- **EvidenceViews** (ObjectiveBreakdownView, ConstraintTraceView) — CP-SAT objective decomposition and constraint trace visualization.
- **Search functionality** — Ctrl+K shortcut, modal, query management.

**What is incomplete**:

- No real backend integration — all services use mock implementations
- No plan comparison workspace (F05) specifically, though `comparePlans` API exists
- No dedicated disruption/recovery workspace UI (though disruption components exist)
- No audit workspace specifically
- Plan comparison UI exists in DecisionCard alternatives but not as a dedicated workspace
- Simulation workspace UI exists but may need enhancement for F06

**UI/UX Observations**:

- **Railway operations aesthetic** — Not a generic SaaS dashboard. Uses muted color palette, status-colored badges, typographic hierarchy consistent with operational software.
- **Human-in-the-loop boundary clearly maintained** — DecisionCard explicitly labels "Human Authorization Required" and requires explicit approval. Never implies automatic execution.
- **Live vs Scenario distinction** — StateBadge and OperationalContext properly tag mode. Scenario mode switches metadata to `'SCENARIO'` and restores to `'LIVE'` on exit.
- **Explainability** — DecisionCard shows primary rationale, expected impact, risk/robustness (Monte Carlo), and constraint trace. Alternatives shown with delta metrics.
- **Impact visibility** — Metric cards and decision evidence show train delays, maintenance completion %, overrun risk %.
- **Decision support not execution** — Approve button labels "Authorize & Approve Plan" not "Execute". Workflow requires human authorization.

---

## 9. Current Testing

**All test suites pass** (9 file, 39 tests):

| Test File | Tests | Status |
|---|---|---|
| `tests/mock-services.test.ts` | 5 | ✅ Pass |
| `tests/api-contracts.test.ts` | 17 | ✅ Pass |
| `tests/contracts-validation.test.ts` | 4 | ✅ Pass |
| `tests/data-table.test.tsx` | 2 | ✅ Pass |
| `tests/decision-card.test.tsx` | 2 | ✅ Pass |
| `tests/state-badges.test.tsx` | 4 | ✅ Pass |
| `tests/search-context.test.tsx` | 2 | ✅ Pass |
| `tests/global-context.test.tsx` | 1 | ✅ Pass |
| `tests/app-shell.test.tsx` | 2 | ✅ Pass |

**Typecheck**: `tsc --noEmit` — passes with no errors

**Lint**: `eslint .` — passes with no errors

**Test infrastructure**: Vitest + React Testing Library

**Known test warnings**: Some tests have "update to OperationalProvider inside a test was not wrapped in act(...)" — these are existing test patterns, not failures.

---

## 10. Current Phase

Based on the repository evidence:

- **Phases P00–P08 are complete** (confirmed by phase reports)
- The frontend has:
  - ✅ Application shell (P02)
  - ✅ Shared domain contracts (P03)
  - ✅ API contracts & service boundaries (P04)
  - ✅ FastAPI backend foundation (P05)
  - ✅ Operations & maintenance backend (P06)
  - ✅ Block planning backend (P07)
  - ✅ Decision & governance backend (P08)
- The immediate frontend work is entering the **intelligence and production-development stage**
- The **Command Center (F02)** is the most complete feature, already integrated with DecisionCard, metric cards, and the human-in-the-loop workflow
- **F01 API Integration** is partially done — the service layer and contracts exist, but real backend connection is the remaining work
- The project is positioned to begin the F01-F10 frontend roadmap, with F02 Command Center being the most advanced

---

## 11. Recommended Next Phase

**Recommendation: F01 API Integration** (with F02 Command Center enhancement)

**Rationale**:

1. The service layer and API contracts are already architected and mocked (F01 foundation complete)
2. The Command Center (F02) is already implemented but relies on mock data — connecting real API endpoints would make it production-ready
3. All 39 tests pass, providing a safety net for integration work
4. The architectural foundation (service container, typed contracts, OperationalContext) is in place
5. The next logical step is replacing mock implementations with real API calls while preserving the existing UI

**Alternative**: If the goal is to advance the roadmap forward, **F02 Command Center → F03 Maintenance Workspace** could proceed in parallel, as the UI components and patterns are already established.

Given the existing code quality and architectural foundation, the most valuable next step is **F01 API Integration** — connecting the service layer to the real FastAPI backend, beginning with the most critical services (network, maintenance, recommendations).

---

## 12. Risks

| Risk | Mitigation |
|---|---|
| **Mock data presented as real intelligence** | Provenance tracking (DataState: REAL/MOCKED/SIMULATED/STUBBED/PLANNED) is already in contracts. UI should display provenance source where relevant. |
| **Scenario state mutating live state** | `ScenarioContext` in every API request enforces mode boundary. OperationalContext switches metadata mode on enter/exit scenario. StateBadge visual distinction enforced. |
| **Human-in-the-loop boundary violation** | DecisionCard explicitly requires callback functions. No auto-execution. Labeling clearly distinguishes "Human Authorization Required" from system execution. |
| **Live/scenario state confusion** | OperationalContext centralizes mode state. StateBadge visual prefix ( LIVE/ ACTUAL/ PRED:/ WHAT-IF:). ScenarioContext on every API request. |
| **ID type confusion** | Branded ID types (`TrainId`, `AssetId`, etc.) prevent cross-assignment. Use factory functions (`makeTrainId`, `makeAssetId`) rather than raw strings. |
| **Over-engineering the UI** | Existing UI follows minimal, operational aesthetic. New work should match this style rather than introducing random complexity. |
| **Backend API changes breaking frontend** | Contracts are the source of truth. Any backend change must update `contracts/api/` first. Typecheck lint catch type mismatches. |

---

## 13. Questions / Blockers

No questions genuinely requiring clarification at this onboarding stage. The repository is well-structured, all tests pass, and the architecture is clear.

If clarification is needed later on:
- Real FastAPI endpoint URLs and auth scheme
- Deployment configuration for production environment
- Specific DataSource labeling requirements for demo vs production data

---

## 14. Changes Made

For this onboarding phase:

**NONE** — No code changes were necessary. The working tree was synchronized to the correct branch (`opencode/frontend`) and the repository state was validated. The onboarding consisted entirely of inspection and analysis.

---