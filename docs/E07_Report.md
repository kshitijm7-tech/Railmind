# E07 — Backend Engine Integration & API Boundary Report

Status: **COMPLETE** · Commit: *this commit* · Branch: `freebuff/engine`

## 1. Executive Summary

E07 exposes the E01–E06 engine through the existing backend as a **thin adapter/orchestration boundary**: `POST /maintenance/prioritize` (E02), `POST /plans/{plan_id}/simulate` and the scenarios family (E05), and `POST /predictions/duration` + `POST /predictions/failure-risk` (E06), all under `/api/v1`. The backend owns HTTP transport, envelope construction, dependency wiring and error mapping only — every calculation is a delegated engine call. **The engine is wrapped, never duplicated** (zero engine math exists in the backend; structurally tested).

## 2. Authoritative specification

- **TRD §37 API Architecture**: base `/api/v1`; the Maintenance family (`POST /maintenance/prioritize`), Plans family (`POST /plans/{id}/simulate`), and Scenarios family (`POST /scenarios`, `POST /scenarios/{id}/simulate`) are the engine-mapped Tier-1 endpoint families.
- **TRD §38**: optimization/simulation should not block HTTP; Tier-1 uses FastAPI (the existing backend is synchronous, matching the existing `AsyncJob` stubs; async/job infra is NOT added — see §11).
- **Blueprint §15** (API surface: `/api/v1/maintenance`, `/api/v1/plans`, `/api/v1/scenarios`).
- **Existing backend architecture** (`app/main.py`, `api/v1/router.py`, `api/dependencies.py`, `core/errors.py`, `api/models.py`): the established envelope (`ApiResponse[T]` + `ApiMeta`), `DomainError` → HTTP mapping, thin routers → services, `/api/v1` prefix — all followed, nothing parallel.
- **Frontend contracts** (`contracts/api/common/envelope.ts`, `contracts/api/endpoints.ts`, `contracts/ai/predictions.ts`): camelCase request/response fields and `PredictionBase` vocabulary are preserved 1:1.
- **Spec silences documented**: no authentication is specified for Tier-1 → none implemented (the envelope contract already carries `actor?` as a placeholder); no persistence for engine results → none added; no E01 constraints endpoint family exists in TRD §37 beyond generate-plan flows already stubbed by P07 → not invented.

## 3. API architecture

```
Client
  ↓
FastAPI router (app/api/v1/endpoints/engine.py)   ← HTTP only: envelope, status codes
  ↓
EngineIntegrationService (app/engine_adapter/service.py)   ← orchestration facade
  ↓
mapper.py (explicit API↔engine field mapping + error translation)
  ↓
engine_bridge.py (the single sanctioned import point — repo-root engine package)
  ↓
RailMind Engine (E02 priority · E05 simulation · E06 prediction)
```

`engine_bridge.py` performs the one-time, documented `sys.path` bootstrap that makes the repository-root `engine/` package importable from the backend process; the backend venv does not install the engine. Every other backend module is forbidden from importing `engine` directly (architecturally tested).

## 4. Endpoints

| Method | Path | Request | Response | Errors | Engine |
|---|---|---|---|---|---|
| POST | `/api/v1/maintenance/prioritize` | `PrioritizeTaskRequest` | `ApiResponse[PrioritizeTaskResponse]` | 400 (INVALID_CRITICALITY, INVALID_PROBABILITY, INVALID_OVERDUE_DAYS*, ENGINE_INPUT_INVALID), 422 (shape) | E02 |
| POST | `/api/v1/plans/{plan_id}/simulate` | `SimulateRequest` | `ApiResponse[SimulateResponse]` | 400 (MISSING_TASK_BANDS, ENGINE_INPUT_INVALID), 422 (shape) | E05 |
| POST | `/api/v1/scenarios` | `{scenarioId}` | `ApiResponse[{scenarioId, status}]` | 400 (INVALID_SCENARIO_ID) | — (identity pass-through) |
| POST | `/api/v1/scenarios/{scenario_id}/simulate` | `SimulateRequest` | `ApiResponse[SimulateResponse]` | 400 / 422 as above | E05 |
| POST | `/api/v1/predictions/duration` | `DurationPredictionRequest` | `ApiResponse[DurationPredictionResponse]` | 400 (ENGINE_INPUT_INVALID incl. deadline-without-start), 422 (shape) | E06 |
| POST | `/api/v1/predictions/failure-risk` | `FailureRiskPredictionRequest` | `ApiResponse[FailureRiskPredictionResponse]` | 400 (ENGINE_INPUT_INVALID), 422 (shape) | E06 |

*overdueDays < 0 rejects at the schema boundary (422) via `ge=0`; the adapter check is defense-in-depth.

## 5. Contract mapping

Explicit, field-by-field in `mapper.py` and the private service builders:
`PrioritizeTaskRequest` → `PriorityInput` (taskId→task_id, failureRisk→AssetFailureRisk, ...); `SimulateBlockRequest` → `BlockWindow` (taskBands→DurationBand list; empty bands refused — the engine never fabricates uncertainty); `DurationPredictionRequest` → `DurationFeatures` + optional `DurationPredictionWindow`; `FailureRiskPredictionRequest` → `FailureRiskFeatures`. Response builders carry the engine result verbatim: every E02 factor contribution, E05 exceedance count/violation-draw index, E06 reason code and all provenance fields survive to JSON. No engine value is invented, defaulted or clamped (§11).

## 6. Provenance

Engine identity survives the full chain `engine → adapter → JSON`: E02 (`priorityModelId`/`priorityModelVersion`/`engineVersion`), E05 (`simulationModelId`/`simulationModelVersion`/`engineVersion` + seed/iterations/distribution), E06 (`modelId`/`modelVersion`/`algorithm`/`engineVersion`). The request path variable (`plan_id`/`scenario_id`) is stamped verbatim as the result's `candidateId` — E05's candidate-association discipline (E05 §14) is preserved at the HTTP boundary. Request correlation (`ApiMeta.requestId`, backend-owned) stays separate from domain provenance (§12) — never merged.

## 7. Error mapping

```
engine ValueError / pydantic ValidationError → DomainError(VALIDATION, ENGINE_INPUT_INVALID) → 400
engine KeyError                              → DomainError(NOT_FOUND, ENGINE_ENTITY_NOT_FOUND) → 404
adapter pre-checks (criticality, probability, bands) → DomainError(VALIDATION, specific codes) → 400
request shape violations (pydantic field constraints) → FastAPI → 422
non-domain exceptions                        → propagate → FastAPI → 500 (no blanket catch)
```

Error responses use the existing `ApiResponse` envelope with `ApiError{code, message, httpStatus}`; the DomainError handler strips all internals (no tracebacks, no paths — tested). The documented taxonomy: **422 = request shape, 400 = engine-contract semantics.**

## 8. Frontend compatibility

- `contracts/api/endpoints.ts` `PLANS_COMPARE`-adjacent simulate and maintenance families are now real: the implemented paths match `POST /maintenance/prioritize` (TRD §37) and the simulate families; the camelCase field names match `envelope.ts` and `predictions.ts` (`probabilityOfFailure`, `modelId`, `timeHorizonHours`, ...).
- Remaining compatibility work (explicitly deferred, §11): the frontend `API_ENDPOINTS` table lists `SIMULATIONS_LIST/DETAIL/RESULT/RUN` async-job endpoints (TRD §38 job architecture) — those require the worker/async decision and scenario state that is deliberately out of E07 Tier-1 scope; no frontend files were modified.

## 9. Testing

- `backend/tests/test_api_engine.py` (31): valid/malformed requests per endpoint, error codes and the 422/400 taxonomy, full E02 explainability through JSON (factor contributions ≈ normalizedScore×weight), provenance identity for E02/E05/E06, seed/iterations pass-through and authoritative defaults (N=200/seed 0), same-seed reproducibility, candidate-id stamping, delegation proofs (API score/probability == direct engine call), determinism across repeated calls, envelope integrity, no stack traces, existing endpoints untouched.
- `backend/tests/test_engine_architecture.py` (16): engine never imports the backend; only `engine_adapter`/`engine_bridge` may import `engine`; bridge imports public contracts only; zero engine-math tokens in the backend; **global RNG state untouched by serving requests**; raw engine error → 400 DomainError envelope at HTTP layer; error translation unit tests (ValueError→400, KeyError→404, DomainError pass-through, unrelated errors propagate); explicit mapping tests incl. `REPAIR` (backend enum member outside the engine vocabulary) rejected loudly with the engine's message — no invented mapping (§11; documented mismatch below).

**Totals: E07 = 47 new backend tests · backend 74 passed (27 baseline + 47) · engine 357 passed (E01–E06 untouched, zero engine-file modifications).**

## 10. REAL / MOCKED / STUBBED

- HTTP boundary (routers, envelopes, 202-free sync semantics, OpenAPI schemas): **REAL**
- Engine delegation (E02/E05/E06 invocation, provenance, error mapping): **REAL**
- Dependency wiring (engine_bridge bootstrap, `get_engine_integration_service`): **REAL**
- Scenario identity pass-through (`POST /scenarios`): **REAL but minimal** — validates and echoes the identity; no state store (by design, see §11)
- MOCKED: none
- STUBBED: none (the pre-existing P07 `generate_plan`/`compare_plans` stubs were NOT touched)

## 11. NOT IMPLEMENTED

- **E04 scenario comparison over HTTP**: E04 consumes caller-supplied `CandidateSolution`+`ObjectiveBreakdown` objects; TRD §37's scenario family covers state (`POST /scenarios`) + simulate, both implemented, but a comparison endpoint would need either a persisted candidate-store or an upload schema carrying full objective breakdowns — the authoritative documents define neither for Tier-1. Documented as the E08/async-phase decision.
- **TRD §38 async job architecture** (`SIMULATION_RUN` → 202 + job polling): the existing backend is synchronous and the authoritative Tier-1 documents do not mandate a worker for the O(N) Monte Carlo pass; adding queues/workers is explicitly out of scope (§30).
- **E01 constraint evaluation endpoint**: TRD §37 has no constraints family; E01 remains internal to the planning pipeline (P07 boundary).
- **Persistence** (no DB for engine results), **authentication** (none specified for Tier-1), **trained ML serving** (E06 registry records models DISABLED — the API honestly serves the deterministic baselines with `algorithm="deterministic-rules"`; no ML availability is claimed), **solver**, **frontend changes**, **WebSockets/workers/MLflow**.

## 12. Known limitations

1. **Task-type vocabulary mismatch (documented)**: the backend `TaskType` enum carries `REPAIR`/`REPLACEMENT`, which are not in the engine's canonical vocabulary (PREVENTIVE|CORRECTIVE|INSPECTION|EMERGENCY|DEFECT). The engine stays the vocabulary authority; such values are rejected loudly (400) rather than mapped to an invented equivalent. Resolution (vocabulary alignment) is a contract-governance decision for the domain owners, not something the adapter should invent.
2. **Stateless scenarios**: `POST /scenarios` registers nothing persistent; scenario state branching (PRD §32/§33) belongs to the state layer (later phase).
3. **Synchronous execution**: all endpoints run inline; large Monte Carlo batch requests are bounded only by the caller's iteration count.
4. **Engine path bootstrap**: `engine_bridge.py` requires the repo-root source tree (documented RuntimeError if absent); the engine is not a packaged dependency of the backend venv.

## 13. E08 boundary

E08 may consume: the six implemented engine endpoints as its client surface; `EngineIntegrationService` as the single orchestration seam (new engine phases slot in behind the same facade + mapper pattern); the error taxonomy (422 shape / 400 engine-contract / 404 missing / 500 internal) and envelope conventions; `engine_bridge.py` as the only sanctioned engine import point; and the provenance-preservation tests as the regression baseline. E08 must not expect: scenario state, async jobs, persistence, authentication, trained-ML serving, or any E01–E06 semantic change from E07.
