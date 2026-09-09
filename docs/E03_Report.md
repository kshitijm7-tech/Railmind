# E03 — Maintenance Optimization Integration Report

Status: **COMPLETE** · Commit: *this commit* · Branch: `freebuff/engine`

## 1. Summary
Implemented the E03 **Optimization Integration Layer** as `engine/optimization/`: a deterministic, inspectable evaluation of candidate maintenance plans against the authoritative **blueprint §17.5 / TRD §25 objective**, consuming E02's `PriorityResult` through its public contract and applying the optimization-level coefficient **β**. No solver, no ML, no LLM, no E04 scope.

## 2. Authoritative specification
- **Blueprint §17.5** (and identical **TRD §25**): the maintenance-optimization objective and its default weights (α=5, β=4, γ=1, δ=2, ε=1, marked [ASSUMPTION] in the blueprint and explicitly designed as UI-exposed configuration).
- **Blueprint §17.3**: decision variables `x[t,w]`, `y[w]`, `unscheduled[t]` — mirrored at the evaluation level by `TaskAssignment`/`BlockActivation`.
- **PRD FR-MI-001** (via E02): the priority signal E03 consumes.
- No conflict between prompt and repository specification was found; where the prompt offered options (tie-breaking, missing-data), the blueprint's silence is honored by neutral defaults documented below.

## 3. Architecture
```
E01 ConstraintEngine → feasibility (unchanged; caller gates candidates)
E02 PriorityEngine   → PriorityResult (public contract, consumed as-is)
E03 ObjectiveEvaluator → ObjectiveBreakdown (per-term §17.5 decomposition)
```
`engine/optimization/` imports **only** the public E02 surface (`engine.priority.result.PriorityResult`) and `engine._version`. E02/E01 import nothing from E03. No circular dependencies. Engine imports only pydantic + stdlib (verified by scan).

## 4. Objective formulation
Exactly as specified (MINIMIZATION; sign convention preserved):

```
Minimize  α·Σ_r delay_r
        + β·Σ_t unscheduled_t · priority_t
        + γ·Σ_w y_w
        + δ·Σ_w y_w · overrun_risk(w)
        − ε·Σ_w bundle_bonus_w
```

- `priority_component_t = β × priority_score_t` — a positive **cost** for leaving high-priority work unscheduled; scheduling a task is implicitly rewarded by avoiding the cost (no sign flip anywhere).
- Bundling is the only reward and is subtracted (−ε), exactly as §17.5 states.
- The total is exposed term-by-term (`train_delay_component`, `priority_component`, `block_count_component`, `overrun_risk_component`, `bundling_component`) plus `total_objective`, so the audit trail never re-derives anything.

## 5. Priority integration
- `TaskAssignment.priority: Optional[PriorityResult]` — the E02 result object itself.
- The primary signal is `priority_score`; `factor_scores[].contribution` is carried **verbatim** into `PriorityComponent.factor_contributions` (never recalculated — enforced by a test that feeds a deliberately hand-crafted result and asserts verbatim propagation).
- `priority_class` is carried for reporting only; the optimizer uses the continuous score.

## 6. β configuration
`OptimizationConfig.unscheduled_priority_weight` (β), default **4.0** (blueprint §17.5/TRD §25). Validation: `ge=0` (β=0 is legal and tested — priority then has zero influence). β is deliberately distinct from E02's internal factor weights; the config exposes no E02 weight fields.

## 7. Hard constraints
Priority never bypasses feasibility. E03 contains **no** feasibility evaluation and no code path touching E01 results; §11's separation is structural (objective layer only) and tested (`test_priority_does_not_bypass_hard_constraints_in_ranking` proves the total decomposes purely into the §17.5 terms). Candidate gating remains the caller's responsibility (future backend integration / P11).

## 8. Explainability
`ObjectiveBreakdown` exposes every §17.5 term, the weights actually used (`weights`), and per-task `PriorityComponent(task_id, priority_score, beta, contribution, factor_contributions, priority_model_id, priority_model_version)` — the full "why was this task favored" chain from E02 factors to objective cost. Deterministic strings/numbers only; no LLM.

## 9. Provenance
E02 lineage (`priority_model_id`, `priority_model_version`) is retained verbatim per component and never overwritten. E03 declares its own identity (`OPTIMIZATION_MODEL_ID = "railmind-optimization-objective"`, version 1.0.0) plus the shared `ENGINE_VERSION`. The two identities coexist explicitly (asserted in tests to differ).

## 10. Tests
`engine/tests/test_optimization_config.py` (8): §17.5 defaults vs blueprint/TRD, weight mapping order, negative-weight rejection, all-zero legality (weighted **sum** needs no mean-normalization unlike E02).
`engine/tests/test_optimization_objective.py` (18): exact §17.5 math incl. full signed-term reconciliation, β semantics (linear scaling, β=0, scheduled→zero), zero/max priority, multi-task summation, delay/block/overrun/bundling terms, ranking with neutral tie-break, determinism (identical model_dump), config immutability.
`engine/tests/test_optimization_contract.py` (18): the §21 boundary — real E02 result flows into E03, missing-priority fail-closed (never a silent 0), factor contributions verbatim (incl. forged-result proof), provenance retention, serializable round-trip, feasibility separation, numerical defense (NaN/inf/out-of-range rejected at every boundary), β ≠ E02 weights, `validate_default` regression.

**Totals: engine 185 passed · backend 27 passed (no regression).**

## 11. REAL / MOCKED / STUBBED
- Objective evaluation: **REAL**
- β/priority integration: **REAL**
- Ranking (deterministic, neutral tie-break): **REAL**
- Input validation/numerical defense: **REAL**
- CP-SAT / OR-Tools solver: **NOT IMPLEMENTED** (out of E03 scope per prompt §10; blueprint assigns solving to the later optimization phase)
- Backend adapter / FastAPI integration: **NOT IMPLEMENTED**
- Delay/overrun/bundle *prediction* models (E05/E06 inputs): **NOT IMPLEMENTED** — those values are accepted as inputs, not produced

## 12. Known limitations
1. **No solver**: E03 *evaluates* candidate solutions; it does not search for them. Candidate generation stays with P07's temporary planner until the agreed future integration.
2. **Tie-breaking**: §17.5 defines none; a neutral `(total_objective, plan_id)` ordering is used and documented — no invented semantic rule.
3. **Single-corridor aggregation**: `total_train_delay_minutes` is accepted as an aggregate per the §17.5 Σ notation; per-route delay attribution is a solver-phase concern.
4. **β/α/γ/δ/ε defaults are blueprint [ASSUMPTION] values**, by design exposed as configuration for the planning UI.

## 13. E04 integration boundary
E04 (Simulation) can consume:
- `ObjectiveBreakdown` as the deterministic evaluation baseline for scenario scoring/comparison;
- `CandidateSolution`/`TaskAssignment`/`BlockActivation` shapes as the vocabulary for "plan under evaluation";
- `rank_candidates` for scenario plan comparison.

E04 must NOT expect: scenario state isolation (E04's responsibility), solver search, or any E03-side persistence. Nothing here touches live state.

## 14. Git
Files added: `engine/optimization/{__init__,configuration,inputs,result,evaluation}.py`, `engine/tests/test_optimization_{config,objective,contract}.py`, `docs/E03_Report.md`.
Files modified: `engine/_version.py` (E03 identity), `engine/__init__.py` (E03 re-exports).
