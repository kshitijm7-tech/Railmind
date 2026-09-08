# E05 — Scenario Risk Simulation & Uncertainty Report

Status: **COMPLETE** · Commit: *this commit* · Branch: `freebuff/engine`

## 1. Summary
Implemented the E05 **Scenario Risk Simulation & Uncertainty Engine** as `engine/simulation/`: the blueprint §17.6 / TRD §26 / PRD §30 **Tier-1 simplified Monte Carlo robustness pass**. Samples task durations from their [P10, P90] bands, re-checks §17.4 constraints **6 and 7** per draw, and reports **P(overrun) per block** and **P(any-plan-violation)** overall, with full sampling evidence (iterations, seed, distribution, exceedance counts, violation draw indexes). All randomness is isolated behind explicit per-window seeds inside one designated module; E01–E04 deterministic semantics are untouched. Stdlib only (no NumPy/SciPy), no solver, no LLM.

## 2. Authoritative specification
- **Blueprint §17.6**: "run N=200 Monte Carlo draws sampling each dur_t from its [P10, P90] band; re-check constraint 6 and 7 under each draw; report P(overrun) per block and P(any-plan-violation) overall."
- **Blueprint §16.1** (Model 1): overrun = "probability duration exceeds latest_finish constraint" — consistent with the c7 reading of the §17.6 event.
- **TRD §26 Robust Scheduling**: N=200; samples from the defined uncertainty band; outputs P(overrun), P(plan violation).
- **TRD §34 config**: `simulation.monte_carlo_runs: 200` — configuration, not a constant.
- **PRD §30 Robustness Requirements**: simplified Monte Carlo, durations sampled from the configured uncertainty range.
- **Blueprint §17.2/§17.4**: `dur_t_p90`, c6 (duration feasibility) and c7 (window bounds, `maxdur_w`) definitions.
- **Spec silences documented** (§43): the distribution *shape* over the band is unspecified → uniform chosen as the least-assumptive default and encoded as an explicit enum; §16.1's expected-duration/P10/P90/confidence *outputs* belong to the XGBoost duration-prediction model (ML track), not to E05; Tier-1 lists no delay-propagation or completion-probability simulation outputs. No conflicts requiring resolution were found.

## 3. Architecture
```
DETERMINISTIC PATH (unchanged)
E01 feasibility → E02 priority → E03 objective → E04 comparison

PROBABILISTIC PATH (new, evidence-only)
Candidate block windows → E05 seeded Monte Carlo → P(overrun)/block
                                                → P(any-plan-violation)
                                                → duration profile per block
```
`engine/simulation/` imports only stdlib + pydantic + `engine._version`. It consumes caller-supplied window/band inputs; it never imports E04's `ScenarioCandidate` types (§16 allows a *narrowly defined* input derived from the candidate — the `BlockWindow` view is exactly that, carrying the caller's candidate/window identity), and never recomputes E02 priority or E03 objective (structurally tested).

## 4. Simulation model
- **Distribution**: `UNIFORM` over each task's `[P10, P90]` band (mandated band; unspecified shape → least-assumptive default, exposed as `DurationDistribution`).
- **Parameters**: `DurationBand(task_id, p10_minutes, p90_minutes)` per task, `BlockWindow(window_id, section_id, earliest_start, latest_end, max_duration_minutes, task_bands)` per block.
- **Sampling**: per draw, one uniform sample per task (stable task order); window total = `math.fsum` of sampled durations.
- **Iterations**: `iterations` (default **200**, authoritative; `>= 1` enforced).
- **Seed**: explicit `seed` in `SimulationConfig` (`>= 0`); each window's stream is derived deterministically via `derive_stream_seed(seed, window_id)` (blake2b as a pure mixer; reported in results). An explicit `seed=` argument to `simulate_block` overrides derivation for manual control.
- **Threshold**: `max_duration_minutes` (§17.4 c7 `maxdur_w`) — the authoritative exceedance threshold.

## 5. Metrics
- **P(overrun) per block** = (# draws violating c6 or c7 for that window) / iterations.
- **P(any-plan-violation)** = (# draws in which ≥1 window violates) / iterations, computed over the shared draw-index space (order-invariant).
- **Per-block duration profile**: expected/min/max/P10/P90 of the per-draw total (`SampleSummary`, nearest-rank percentiles), plus per-constraint exceedance counts (`c6_duration_feasibility`, `c7_window_bounds`) and the exact violating draw indexes (auditable, reproducible).
- No confidence intervals (not specified — §32), no invented metrics.

## 6. Reproducibility
Same (inputs, config, seed) → byte-identical result (tested via `model_dump` equality, including through `simulate_plan`). Different seeds *may* differ and here statistically do. The global `random` state is never touched: a local `random.Random` per stream (state-untouched test included).

## 7. Deterministic/probabilistic boundary
E05 writes nothing back: it never mutates inputs (frozen models + immutability test), never replaces E04's `objective_delta_from_best`/breakdown, never reruns or reimplements E03's formula (source-scanned), never alters E02 scores. It produces **additional evidence** alongside the deterministic baseline. Risk-adjusted ranking is **not** implemented — the specification assigns none (§29).

## 8. Provenance
`SIMULATION_MODEL_ID = "railmind-monte-carlo-robustness"`, `SIMULATION_MODEL_VERSION = "1.0.0"` on every result, plus `engine_version`. Upstream lineage is preserved by reference: results carry the caller's `candidate_id` (E04 identity) and per-window ids; nothing upstream is overwritten. E05 adds its identity to the chain rather than replacing any layer.

## 9. Validation
Strict, loud, no clamping: iterations `< 1` and non-integer rejected (zero draws would divide by zero — §22); seed `>= 0`; band values finite and positive with `p10 ≤ p90` (never reordered); window bounds ordered, `max_duration_minutes` finite/positive; duplicate `window_id`s rejected in batch; NaN/±inf rejected everywhere; probabilities structurally bounded `[0, 1]` (pydantic `ge/le`) and empirically exact (draws/iterations).

## 10. Tests
`test_simulation_config.py` (12): authoritative defaults (200/UNIFORM), valid iteration/seed values, rejected 0/negative/non-integer iterations, negative seed, p10>p90 rejection, degenerate band, window bounds validation.
`test_simulation.py` (26): reproducibility (block + plan), different-seed divergence, global-RNG isolation, P(overrun) ∈ [0,1] across seeds, **zero-overrun** and **certain-overrun** cases, exact draws/iterations denominator, sampled totals within band sums, degenerate-band exactness, input immutability, no-upstream-reimplementation scan, expected-duration convergence to the analytic uniform midpoint, convergence (N=50 vs N=5000), candidate-id preservation, stream-seed determinism, batch coverage, **solo == batch** identity, **order invariance** (forward/backward), subset independence, NaN/±inf/duplicate rejection, closed-form overrun check for a sum of two uniforms (P(T1+T2>78)=1−455.5/600≈0.2408, tolerance 4σ), percentile ordering + known nearest-rank values, serialization round-trip with provenance, and an N=200×10-window performance bound.
`test_simulation_contract.py` (8): AST-level RNG containment (RNG *only* in `distributions.py`; docstrings can't false-positive), no RNG leak into E01–E04, no E01–E04 module imports E05, no E02/E03 logic duplication, exact E05 export surface, provenance identity, full evidence presence (iterations/seed/distribution/exceedance keys/draw indexes), export hygiene.

**Totals: engine 290 passed (228 baseline + 62 E05) · backend 27 passed (no regression).**

## 11. Performance
O(iterations × tasks) per window; single process; `math.fsum`; no per-draw object churn beyond tuples. The N=200 authoritative configuration over 10 windows completes in milliseconds (bounded by test at < 5 s, orders of magnitude above observed).

## 12. REAL / MOCKED / STUBBED
- Seeded Monte Carlo sampling: **REAL** (stdlib `random.Random`, uniform over [P10, P90])
- c6/c7 re-checks: **REAL**
- P(overrun)/block, P(any-plan-violation): **REAL**
- Duration profile (mean/min/max/P10/P90, nearest-rank): **REAL**
- Seed/stream management and reproducibility: **REAL**
- Validation/numerical safety: **REAL**
- XGBoost duration prediction (§16.1): **NOT IMPLEMENTED** (E05 consumes bands; the ML model is a separate track)
- Delay propagation / maintenance-completion probability (TRD §26 outputs): **NOT IMPLEMENTED** (requires the L7 discrete-event network model — later phase)
- Scenario state branching / copy-on-write (PRD §32/§33): **NOT IMPLEMENTED** (state layer's responsibility; E05 samples, it does not branch state)
- Risk-adjusted ranking / recommendation decision: **NOT IMPLEMENTED** (no spec support)
- Solver, API, persistence, LLM: **NOT IMPLEMENTED** (as before)

## 13. Known limitations
1. **Uniform band shape is an assumption** — the spec mandates the band, not the shape; uniform is the least-assumptive choice and `DurationDistribution` exists so a spec-backed alternative can be added without contract churn.
2. **c6/c7 checked under a sequential-execution model** — the window span equals the summed sampled durations; per-crew parallel bundling (Tier 2 refinement of §17.4 c6) is not simulated.
3. **No intra-window scheduling** — a full start/end rescheduling model per draw is Tier 2; E05 evaluates threshold exceedance, not detailed timetables.
4. **`derive_stream_seed` uses blake2b** purely as a deterministic (seed, window_id) mixer into the 63-bit seed space; any hash would do — documented so the choice isn't mistaken for a security feature.
5. **Band inputs are caller-supplied** — if upstream P10/P90 data is missing, callers must supply sensible bands or the pass cannot run; E05 does not fabricate uncertainty.

## 14. E06 boundary
E06 (Risk Prediction) can consume:
- `PlanSimulationResult` / `BlockRiskProfile` as the simulation-evidence baseline (P(overrun), exceedance counts, duration percentiles) for model-driven risk scoring;
- `SampleSummary` percentiles as calibrated uncertainty inputs;
- `SimulationConfig` seed discipline as the reproducibility precedent for any stochastic E06 work.

E06 must NOT expect from E05: ML failure-risk models (E06 owns those per §16), state branching, live-data ingestion, or any persistence/API. E05 deliberately stops at producing deterministic-given-seed simulation evidence.
