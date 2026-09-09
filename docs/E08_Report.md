# E08 — Live API Integration, End-to-End Validation & Runtime Hardening Report

Status: **COMPLETE** · Commit: *this commit* · Branch: `freebuff/engine` (not pushed)

## 1. Executive Summary

E08 proves and hardens the E07 architecture as a real running application — **without rewriting it**. The `router → EngineIntegrationService → mapper → engine_bridge → engine` boundary is preserved exactly; E08 adds the runtime layer around it:

- **Live runtime verification**: the canonical `uvicorn app.main:app` server was started and every engine endpoint family was exercised over **real HTTP** (curl, separate process, real sockets) — not only through the test client.
- **CORS** (TRD §46 Tier-1): environment-configured exclusively (`RAILMIND_CORS_ALLOWED_ORIGINS`); secure default = no CORS middleware at all; wildcard-mixed-with-origins rejected at startup.
- **Structured JSON request logs** (TRD §47 Tier-1): one line per request with timestamp/service/run_id/method/path/status/duration_ms/engine_phase, plus `X-Request-Id` response correlation — verified emitted by the live server.
- **Startup verification** (§5/§15): the engine bridge initializes at application startup — a missing/broken engine fails the process at boot, so the service can never report healthy while startup is broken.
- **Runtime/smoke test suite**: 21 tests exercising the real ASGI application boundary, plus a CORS matrix, observability contract tests, and an OpenAPI contract gate.

Nothing else changed: no persistence, no async jobs, no solver, no new ML, no engine modifications (zero engine-file edits), no new dependencies.

## 2. Authoritative Specification

| Source | Use in E08 |
|---|---|
| TRD §46 (API Security, Tier-1 subset) | CORS restrictions via environment; secrets not committed; structured error envelope (already present) |
| TRD §47 (Observability, Tier-1) | Structured JSON logs (timestamp/service/run_id/duration_ms/status) + latency tracking for API/simulation/prediction; explicit non-goal: OpenTelemetry/Prometheus (Tier 2+) |
| TRD §48 (Tier-1 performance) | "UI < 1 second" — measured as a smoke guard only; no invented benchmark targets |
| E08 prompt §5/§15 | Startup verification incl. engine-bridge initialization; never report healthy if startup is broken |
| E08 prompt §8 | OpenAPI contract verification |
| PRD | No service-readiness endpoint specified → none invented; existing `/health` retained unchanged |

Conflicts: none found. Where the prompt offered optional scope (readiness endpoints, Docker, request-ID frameworks), it was not in the authoritative spec and was **not** implemented.

## 3. Runtime Architecture

Unchanged from E07 (§4 hard rule — no rewrite):

```text
HTTP request
   ↓
FastAPI (app.main:create_app)
   ├─ RequestObservabilityMiddleware   ← E08: correlation + §47 JSON log + latency
   ├─ CORSMiddleware                   ← E08: only when env-configured (§46)
   └─ DomainError handler → error envelope
   ↓
API router /api/v1 (unchanged)
   ↓
EngineIntegrationService (unchanged)
   ↓
mapper (unchanged)
   ↓
engine_bridge (unchanged; now probed at startup)
   ↓
RailMind Engine E01–E06 (unchanged, 357 tests green)
```

`main.py` was converted to a `create_app()` factory with a module-level `app = create_app()` — zero default-behavior change; the factory exists solely so the CORS/observability matrix is honestly testable per configuration.

## 4. Startup

Canonical command (unchanged from the repository's existing convention):

```bash
cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Startup sequence (verified live): `configure_logging()` → `RuntimeContext.from_env()` → **engine-bridge import probe** (fails the process at boot if the engine is missing) → middleware assembly → router registration.

## 5. API Verification — live server (real HTTP)

All checks below ran against a real `uvicorn` process on 127.0.0.1 (curl, separate process):

| # | Check | Result |
|---|---|---|
| 1 | `GET /health` | 200, `{"data":"OK"}` |
| 2 | `POST /api/v1/maintenance/prioritize` | 200 — score 0.6667, class HIGH, full factor contributions, missing-data policy, explanation, E02 provenance |
| 3 | `POST /api/v1/plans/LIVE-PLAN/simulate` | 200 — iterations 200, seed 7, P(overrun)=0.0, per-window P10/P90/exceedances, E05 provenance |
| 4 | `POST /api/v1/predictions/duration` | 200 — 113.85 = 90 × 1.10 × 1.15 (exact engine formula), `algorithm="deterministic-rules"` |
| 5 | `POST /api/v1/predictions/failure-risk` | 200 — probability in [0,1], risk class, `algorithm="deterministic-rules"` |
| 6 | Semantic violation (`criticality:"URGENT"`) | **400** with `INVALID_CRITICALITY` engine message |
| 7 | `X-Request-Id` header | present and unique per request |
| 8 | §47 JSON log line from the live server process | verified: `{"timestamp":...,"service":"railmind-backend","run_id":...,"method":"POST","path":"/api/v1/predictions/failure-risk","status":200,"duration_ms":28.817,"engine_phase":"E06"}` |

Classification honesty (§33): these endpoints are **runtime-verified** (real HTTP server), **integration-tested** (ASGI suite), and **unit-tested** (engine + backend suites).

## 6. Contract Verification

`JSON request → API schema → engine input → engine result → mapper → JSON response` is pinned by tests: camelCase field names throughout, engine-required numerics stay required (no silent defaults), enum vocabularies enforced, probabilities structurally bounded, provenance fields (`*ModelId`, `*ModelVersion`, `engineVersion`) survive to JSON. OpenAPI gate: all six engine routes + `/health` + `/api/v1/version` registered with request/response models; no internal routes or engine classes exposed.

## 7. Error Verification

Taxonomy unchanged and live-tested: **422** = request shape (FastAPI/Pydantic boundary); **400** = engine-contract semantics (envelope `error.code`, authoritative engine message preserved, no tracebacks/paths — asserted); **404** = unknown routes; **500** = unexpected failures with `raise_server_exceptions=False` semantics (no blanket `except`, no internals leaked).

## 8. Provenance Verification

End-to-end tests assert E02 (`railmind-deterministic-priority`), E05 (`railmind-monte-carlo-robustness`), E06 (`railmind-duration-prediction` / `railmind-failure-risk-prediction`) identity + versions + `engineVersion` arrive intact in JSON. Request correlation (`X-Request-Id`) is transport-only and asserted never to intersect domain provenance. `recorded_at` remains caller-supplied (engine reads no clock); the backend invents no timestamps.

## 9. Determinism

Same request → byte-equivalent domain payload, asserted for prioritize and simulate. E05 evidence identical across repeated calls with the same seed/iterations. Backend executes **zero** RNG: global `random.getstate()` is pinned before/after live traffic.

## 10. E06 Model Availability

Unchanged truth: `deterministic baseline = available` (verified live, `algorithm="deterministic-rules"`); `trained ML = unavailable` — no artifacts exist, none fabricated, no metrics invented.

## 11. Tests

| Suite | Command | Result |
|---|---|---|
| Engine (E01–E06) | `python -m pytest engine/tests` | **357 passed** |
| Backend (E07 + E08 + baseline) | `backend/.venv: pytest tests` | **106 passed** (27 baseline + 47 E07 + 32 E08) |

E08's 32 new backend tests: runtime smoke (real ASGI: endpoints, error paths, determinism, provenance, performance guard) 21 · CORS matrix 5 · observability 3 · OpenAPI 3.

## 12. REAL / MOCKED / STUBBED

- **REAL**: the running FastAPI application (live uvicorn + curl verification); the full HTTP→engine path; CORS configuration; structured logging; request correlation; all test suites.
- **MOCKED**: nothing.
- **STUBBED**: nothing.

## 13. NOT IMPLEMENTED

- Service-readiness endpoint (no authoritative spec; `/health` retained as-is)
- OpenTelemetry/Prometheus (TRD Tier 2+)
- Docker/containerization, deployment configuration (not in E08 spec)
- Persistence, async jobs, solver, trained ML, frontend UI wiring (explicit non-goals)
- Frontend data-layer connection (deferred — documented, not started)

## 14. Known Limitations

- Live verification used loopback HTTP from a separate process, not an external network hop; results are otherwise identical to deployment behavior.
- CORS wildcard (`*`) is accepted explicitly but disables credentials by design; mixing `*` with origins is rejected.
- `X-Request-Id` is generated per request via `uuid4` (stdlib-internal generator; global RNG state untouched — tested).
- Performance checks are smoke guards (< 1 s), not benchmarks; TRD §48's only Tier-1 figure is respected.

## 15. E09 Boundary

E09 may consume: the verified `create_app()` factory pattern, the runtime settings snapshot (`RuntimeContext`), the observability middleware (§47 fields are stable), the CORS contract (env-only), the smoke-test suite as a regression gate, and the provenance-preserving adapter boundary. E09 must not expect: persistence, queues, metrics backends, auth, readiness probes, or any engine semantic change from E08.
