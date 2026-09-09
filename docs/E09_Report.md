# E09 — CP-SAT Optimization Engine & §16.3 Delay Baseline Report

Status: **COMPLETE** · Branch: `freebuff/engine` · Checkpoint commit: `a4253c0` · Final commit: *this commit* · **Not pushed**

---

## 1. E09 Summary

E09 closes the last two gaps in TRD §73's "Model Count — Final Recommendation" for the first implementation: the **CP-SAT optimization engine** (blueprint §17.1–§17.3, deferred since E03/E04's explicit "no solver invention" boundary) and **Model 3, the §16.3 train-delay baseline** (deferred in E06), exposed through the existing E07/E08 backend boundary as **`POST /api/v1/plans/generate`** (TRD §37's exact, previously unimplemented route).

The E01–E08 chain is preserved verbatim: the planner consumes E02 `PriorityResult`s as-is (§17.2 `priority_t`), ranks every candidate with **E03's exact §17.5 evaluator** (never re-derived), consumes §16.3 delay predictions as computed, and emits a TRD §67 reproducibility record. With E09, the engine delivers: rules layer (E01) + 4 ML models (E02 priority, E06 duration, E06 failure-risk, E09 delay baseline) + **1 CP-SAT optimization engine** + simulation (E05) + Monte Carlo (E05) + **1 graph propagation engine** (E09 NetworkX baseline).

## 2. Authoritative Sources

- **TRD §22–§25**: Tier-1 scheduling engine = CP-SAT (OR-Tools); decision variables `x[t,w]`, `y[w]`, `start/end[w] ∈ ℤ`; hard constraints; §17.5 objective.
- **TRD §26 NFR / blueprint §26**: full solve < 10 s, deterministic (`same seed → same outcome`).
- **TRD §37**: `POST /plans/generate` under the Plans family — the exact route implemented.
- **TRD §65**: configuration architecture — `optimization.timeout_seconds: 10`, objective weights as configuration, "do not hard-code … store them in configuration".
- **TRD §67**: reproducibility contract — every run records all model versions + seed.
- **TRD §70 DoD**: "CP-SAT works, hard constraints enforced, objective works, alternatives generated" (+ "delay model works").
- **TRD §72**: locked stack — OR-Tools CP-SAT + NetworkX (installed; backend `requirements.txt` updated).
- **TRD §73**: model count — the acceptance baseline E09 completes.
- **Blueprint §16.3/§16.4**: Model 3 inputs ("proposed block window, section, affected train IDs, train priority, historical delay patterns for the section, time of day") and the mandate to build the NetworkX graph-propagation baseline **first** ("explainable and always finishes on time").
- **Blueprint §17.1–§17.3**: sets (T, W, R, D), parameters (`dur_t`, `crew_t`, `avail_d,shift`, `[e_w, l_w]`, `maxdur_w`, `delay_pred(w,r)`, `dep(t,t')`), decision variables.
- **Blueprint §17.4** (already E01's validation rules, now the solver's hard constraints c1–c9) and **§17.5** (objective — E03's evaluator).
- **PRD §29**: "a recommended plan plus alternatives" — the `alternative_count` semantics (N plans **alongside** the best).
- **TRD §12**: sizing anchor for the performance fixture (22 tasks / 9 sections / 4–6 windows per section-day / 72 h horizon).
- **TRD §50/§51**: no trained Model 3 artifact exists → honest `deterministic-rules-graph-propagation` labeling.

No conflicts between sources were found; where the blueprint and TRD overlap they agree.

## 3. Scope

**Engine (new packages):**
- `engine/delay/` — §16.3 baseline: `DelayFeatures` (exact documented feature list), `DelayModelConfig` (disclosed [ASSUMPTION] coefficients), `GraphPropagationDelayModel` (direct + bounded NetworkX downstream propagation, priority protection), `DelayPredictionResult` (per-train records with classification/hops/protection factor; total; confidence; honest algorithm label).
- `engine/planner/` — §17.1–§17.3 contracts (`TaskInput`, `WindowInput`, `CrewPool`, `PlannerInput` with cross-reference integrity), `PlannerConfig` (TRD §65 execution settings; E03's `OptimizationConfig` embedded — single source of §17.5 weights), `PlannerModel` (CP-SAT encoding of c1–c9 + §17.3 variables), `CpSatPlanner` (k-best enumeration via no-good cuts, timing-tightening pass, extraction, exact E03 evaluation, TRD §67 evidence), `PlannerError`.

**Backend (existing architecture extended, not replaced):**
- `engine_bridge.py`: E09 public contracts added to the sanctioned import surface.
- `engine_adapter/mapper.py`: explicit field-by-field API↔engine mapping; the §16.3 delay pass runs inside the adapter's engine-delegation boundary; E02 responses are reconstructed into engine `PriorityResult`s **verbatim** (factor provenance + model identity).
- `engine_adapter/service.py`: `generate_plan` — only explicitly supplied request fields override TRD §65 defaults (frozen-config rebuild, never mutation).
- `api/schemas/engine.py`: `PlanGenerationRequest`/`PlanGenerationResponse` family (camelCase, envelope-compatible).
- `api/v1/endpoints/engine.py`: `POST /plans/generate` (thin router — HTTP only).
- `core/runtime.py`: `/plans/generate` → `engine_phase="E09"` (ordered before the `/plans/` E05 prefix; E05 attribution regression-tested).

## 4. Non-Goals (intentionally not implemented)

- No solver *search* beyond what §17 defines (no column generation, no MIP, no metaheuristics) — CP-SAT is the TRD §22 engine.
- No trained Model 3 / gradient-boosted delay model (no artifact exists; TRD §50 — the deterministic baseline is the honest Tier-1 implementation of the §17 TRD interface).
- No plan persistence (TRD §37's `GET /plans/{id}`, `/approve`, `/reject` remain the P07-era in-memory stubs — E09 adds no state).
- No train re-sequencing model (Tier 1 reads §17.5's delay term conservatively: every activated window's predicted delay counts — documented in the solver).
- No async job system (the pre-existing `/planning/generate` 202-AsyncJob stub is untouched P07 scope).
- No frontend changes (not in E09 scope).
- No Docker/K8s/auth/telemetry-framework additions (E08 boundary preserved as-is).

## 5. Architecture

```text
Client
 ↓
FastAPI  (POST /api/v1/plans/generate — thin router, E09 phase attribution)
 ↓
EngineIntegrationService.generate_plan
 ↓
mapper.request_to_planner_input        ← verbatim E02 responses; §16.3 delay pass
 ↓                                       (GraphPropagationDelayModel) inside the
 ↓                                       adapter's delegation boundary
engine_bridge                          (the single sanctioned import point)
 ↓
CpSatPlanner.plan                      (§17.3 variables, c1–c9 hard constraints,
 ↓                                      k-best no-good cuts, timing tightening)
E03 ObjectiveEvaluator                 (exact §17.5 ranking — never re-derived)
 ↓
PlannerResult + TRD §67 evidence
 ↓
mapper.planner_result_to_response → JSON (camelCase, ApiResponse envelope)
```

Dependency direction unchanged: `backend → engine` only; architecture tests now also pin that the backend never imports `ortools`/`networkx`/`cp_model` and that E09's engine modules never import the backend.

## 6. Contracts

**Request** (`PlanGenerationRequest`): `planRef?`, `tasks[]` (`taskId`, whole-`durationMinutes` per §17.3 integer encoding, `department`, `crewSize`, **verbatim E02 `PrioritizeTaskResponse` as `priority`**, `latestFinish?`, `precedes[]`), `windows[]` (`windowId`, `sectionId`, `[earliestStart, latestEnd]`, `maxDurationMinutes`, `qualifiedDepartments[]`, `bundleBonus`, `overrunRisk`), `crewPools[]`, `delayInputs{windowId → §16.3 features}`, optional explicit overrides `timeoutSeconds`/`alternativeCount`/`randomSeed`.

**Response** (`PlanGenerationResponse`): `bestPlanId`, `plans[]` (`planId` `{planRef}-alt{rank}`, `assignments[]` with explicit unscheduled (`windowId: null`), `blocks[]` with timing/assigned work/verbatim `delayEvidence`, `unscheduledTaskIds[]`, E03 `objective` (§17.5 decomposition + weight provenance), `constraintTrace[]` (§17.4 binding/active facts)), `evidence` (TRD §67: solver+version, seed, timeout, status, wallTimeMs, weights, constraint-set + engine + planner identity).

**Validation / errors**: 422 malformed schema; 400 engine-contract violations (`PRIORITY_TASK_MISMATCH`, `DELAY_INPUT_UNKNOWN_WINDOW`, `ENGINE_INPUT_INVALID` — incl. duplicate ids, inverted window bounds, unknown precedence refs, fractional minutes); no stack traces/paths/internals in any error body.

**Provenance**: E02 model identity rides on unscheduled tasks through E03's β-term detail; §16.3 model identity + per-train evidence ride on activated blocks; TRD §67 record carries constraint-set/engine/planner versions + seed. Nothing is re-ranked, re-timed, re-seeded or re-derived by the backend.

**Determinism**: CP-SAT pinned `num_workers=1` + explicit `random_seed` (TRD §67/blueprint §26); k-best cuts are order-deterministic; plan ids renumbered by final E03 rank; identical live-HTTP requests → identical domain payloads (wall time is the only genuine measurement). The delay model is pure (no RNG, no clock, no I/O).

## 7. Testing

- **Engine**: `engine/tests` — **422 passed** (357 E01–E08 baseline + 65 E09: planner semantics c1–c9, k-best/alternatives, timing tightening, E03 ranking integration, determinism, §17.3-slack unschedule-not-infeasible, contract/architecture scans, delay-model semantics/propagation decay/affinity/priority protection).
- **Backend**: `backend/tests` — **126 passed** (106 E07/E08 baseline + 20 E09: 17 API integration tests over the real bridge + architecture extensions + the E09 runtime smoke test).
- **Runtime verification**: real uvicorn (`uvicorn app.main:app`, the canonical E08 command) on loopback; `POST /api/v1/plans/generate` exercised over actual HTTP: HTTP 200, `X-Request-Id`, OPTIMAL status, hand-checkable §17.5 math (total 14.7 = 5×2.82 delay + 1×1 block − 1×0.4 bundling), §16.3 evidence (2.82 = 12 × 0.25 × 0.94), timing-tight block (65-min span for 65-min work), byte-identical determinism, 400 `ENGINE_INPUT_INVALID` error path, live `engine_phase="E09"` JSON log lines. No orphan processes after teardown.

Test layers preserved (prompt §21): engine unit (E09 engine tests) / integration (backend API over the real bridge) / runtime-smoke (real ASGI boundary in `test_runtime_smoke.py` + the live server run documented here).

## 8. REAL / MOCKED / STUBBED

**REAL:**
- CP-SAT solving, §17.4 hard constraints, k-best alternatives, §17.5 E03 ranking, TRD §67 evidence (OR-Tools 9.14).
- §16.3 graph-propagation delay baseline (NetworkX 3.6.1 adjacency BFS, disclosed coefficients).
- HTTP boundary, mapping, error taxonomy, phase attribution, provenance round-trips, determinism — live-verified.

**MOCKED:** nothing.

**STUBBED:** nothing.

(Honesty note: the *delay model* is a deterministic-rules baseline by explicit design — TRD §50/§51 document that no trained Model 3 exists; it is the real Tier-1 implementation of the §16.3/§17 interface, not a stub of a planned model. The `algorithm` field reports `deterministic-rules-graph-propagation` truthfully.)

## 9. NOT IMPLEMENTED (deferred, documented)

- `GET /plans/{id}`, `POST /plans/{id}/approve|reject` (persistence family — P07 stubs untouched).
- Trained Model 3 (XGBoost/GBM delay model), GNN delay propagation (PRD Phase 9 Tier 2).
- Train re-sequencing inside the §17.5 delay term (Tier-1 conservative reading).
- Async plan generation (the pre-existing 202-AsyncJob `/planning/generate` stub).
- Frontend wiring of the new endpoint.

## 10. Known Limitations

- **[ASSUMPTION] delay coefficients**: `base_direct_factor=0.25`, `propagation_factor=0.5`, `priority_attenuation=0.06`, `peak_window_start/end=480/1140`, `peak_adjustment=0.25`, `max_propagation_depth=3`, `priority_scale=5.0` — disclosed, validated configuration (`DelayModelConfig`), never hard-coded at call sites; a trained Model 3 replaces them without contract churn.
- **Tier-1 c8 semantics**: precedence is enforced between windows (`start[after] ≥ end[before]`); intra-window ordering is not modeled (c8 forbids same-window co-assignment of precedence-linked tasks — tested).
- **k-best quality**: alternatives are next-best distinct *activation patterns* under the solver's integer-scaled objective (α/δ/γ/ε/β terms ×100); CP-SAT's internal scaling can differ from E03's float total at sub-0.01 granularity — E03 always provides the authoritative ranking.
- **Time budget**: `timeout_seconds` (default 10) is the *whole-run* budget across enumeration + extraction + evaluation with a 0.5 s evaluation reserve; the §12-sized perf test passes inside it (~9.8 s).
- **Delay-assignment linkage**: CP-SAT steers on per-window delay totals (`Σ_r delay_pred(w,r)`), not per-(window,train) terms; per-train resolution is carried as evidence rather than solver structure (documented Tier-1 simplification).

## 11. E10 Boundary

E10 may consume:
- `engine.planner` public surface (`PlannerInput`, `PlannerConfig`, `CpSatPlanner`, `PlannerResult`, `PlannerError`) and `engine.delay` (`GraphPropagationDelayModel`, `DelayFeatures`, `DelayPredictionResult`) — through `engine_bridge` only.
- `POST /api/v1/plans/generate` as a stable TRD §37 contract (camelCase, envelope, 400/422 taxonomy).
- The TRD §67 evidence record as the canonical "which versions+seed produced this plan" audit anchor.
- `alternative_count` semantics (N alongside the best; PRD §29).

E10 must **not** assume:
- Any persistence of generated plans (stateless by design; E07/E09 boundary).
- A trained delay model exists (check `DelayPredictionResult.algorithm`).
- Intra-window task ordering, re-sequencing, or per-(window,train) solver structure.
- The solver exposes per-constraint duals/shadow prices (CP-SAT feasibility-oriented; the constraint trace is the explainability surface).
- Any change to E01–E08 contracts (all preserved verbatim).
