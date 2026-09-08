# E04 — Scenario Evaluation & Plan Comparison Report

Status: **COMPLETE** · Commit: *this commit* · Branch: `freebuff/engine`

## 1. Summary
Implemented the E04 **Scenario Evaluation & Plan Comparison Layer** as `engine/scenario/`: deterministic ranking of candidate maintenance plans/scenarios by the authoritative §17.5 objective, with a fully preserved E03 breakdown per candidate, exact deltas vs the best, a neutral structured winner summary, and an unbroken E02 → E03 → E04 provenance chain. No solver, no ML, no LLM, no persistence, no API.

## 2. Authoritative sources
- **PRD §29 "Plan Comparison"**: for each optimization run the system produces a recommended plan plus alternatives, per-plan objective score and constraint status; "the user must be able to compare plans".
- **Blueprint §19.1/§19.2**: "Simulate candidates → Rank by objective (§17.5) → Recommend → Human Approval" — ranking criterion is the §17.5 objective, minimization.
- **Blueprint §21 / TRD §34**: recommendation evidence includes `objective_breakdown` and `alternatives — top-3 ranked with their deltas` → per-term deltas and breakdown preservation are required, not optional.
- **TRD §31/§32**: "Rank candidates" is the pipeline step after simulation/Monte Carlo.
- **PRD §33 / blueprint §20**: scenario isolation is copy-on-write at the state layer — E04 performs no state mutation by construction (pure functions over immutable inputs).
- No conflict was found between prompt and repository specification; where the prompt offered options (empty set, duplicates, feasibility representation), the spec's silence is honored with the smallest deterministic behavior, documented below.

## 3. Architecture
```
E01 ConstraintEngine → feasibility (caller gates candidates; unchanged)
E02 PriorityEngine   → PriorityResult
E03 ObjectiveEvaluator → ObjectiveBreakdown  (single source of truth for §17.5)
E04 ScenarioComparator → ScenarioComparison (ranked candidates + summary)
```
`engine/scenario/` imports only E03's public surface (`engine.optimization.inputs/result/configuration/evaluation`) and `engine._version`. Dependency direction E04 → E03 → E02 is enforced by tests (no back-imports, no private reach-ins). E04 never re-derives the objective formula: `evaluate_candidates()` delegates every calculation to E03's `ObjectiveEvaluator`.

## 4. Input contract
- `ScenarioCandidate(candidate_id, solution: CandidateSolution, objective: ObjectiveBreakdown)` — frozen; `candidate_id` is caller-supplied, validated non-empty; E04 never generates IDs.
- `validate_candidates()` guard + comparator-side checks: every objective component must be finite.
- Reuses E03's `CandidateSolution`/`TaskAssignment`/`BlockActivation` verbatim — zero duplicate schedule/task models.

## 5. Ranking semantics
- **Minimization** (§17.5): lower total objective = better; rank 1 = lowest.
- Sort key: `(total_objective, candidate_id)` — ties resolve by ascending neutral identifier, matching the ordering already established by E03. Insertion order, hash order, randomness and invented semantic-importance rules are all excluded (tested via 12 input permutations).

## 6. Feasibility semantics
E04 ranks the candidates the caller supplies and consumes **no** E01 results — there is no feasibility field on `ScenarioCandidate` (structurally tested) and no invented infinity penalty. Per PRD §29, "Constraint status" is reported per plan by the integrating backend (which owns E01); the architectural contract is that **the caller excludes infeasible candidates before comparison** (E01 gate → E03 evaluation → E04 comparison). This assumption is documented rather than duplicated inside E04.

## 7. Explainability
Every ranked entry retains the **complete** `ObjectiveBreakdown` (all five §17.5 components + total + per-task priority contributions + weights actually used) plus the full `CandidateSolution` — never reduced to `candidate_id → float`. `ComparisonSummary` adds:
- `component_deltas` — winner − runner-up per §17.5 term (exact);
- `total_objective_delta`;
- `deciding_components` (terms the winner wins on) and `wins_despite` (terms the winner actually loses but overcomes on aggregate — the audit trail never hides a loss);
- a `statement` string derived purely from the numbers (rounded `_fmt`), no invented semantics, no LLM.

## 8. Provenance
Chain preserved untouched and tested end-to-end, including through serialization: E02 (`priority_model_id`/`priority_model_version` inside E03's `PriorityComponent`) → E03 (`optimization_model_id`/`optimization_model_version`, `engine_version` on breakdown and ranked entries) → E04 (`SCENARIO_MODEL_ID = "railmind-scenario-comparison"`, `SCENARIO_MODEL_VERSION = "1.0.0"` on comparison and ranked entries). E04 rewrites nothing.

## 9. Determinism
Pure functions of (candidates, configuration). Verified by: identical-input identity test, 12-permutation invariance test, forbidden-API source scan (no `datetime.now`/`random`/`uuid`/`time.time` in any scenario module), and package-level grep. Empty set and duplicate IDs are loud validation errors; NaN/±inf are rejected at the boundary (total and every component), never zeroed or clamped.

## 10. Tests
`engine/tests/test_scenario_comparison.py` (26): the full §28 matrix — empty set, single candidate, two/multiple candidates, exact tie, duplicate IDs, NaN/±inf (total + each of the 5 components), breakdown preservation, provenance survival, verbatim priority propagation, input immutability (byte-identical after ranking), determinism, permutation invariance, exact delta math, feasibility policy structure, 200-candidate deterministic set, 1e-9 float ordering, serialization round-trip, monotonic ordering, stable ties, and end-to-end agreement with manual E03 math (incl. custom β and a β=0 tie case).
`engine/tests/test_scenario_contract.py` (12): public-contract-only imports, real-E03-evaluator wiring (identical numbers to manual evaluation), dependency direction (no back-imports), no α/β/γ/δ/ε duplication in E04's surface, weights visible only through E03's results, full provenance chain intact + through serialization, summary deltas derived-not-invented, `wins_despite` populated correctly, single-candidate summary shape, forbidden-API scan, export surface check.

**Totals: engine 228 passed (185 baseline + 43 E04) · backend 27 passed (no regression).**

## 11. Performance
Ranking is a single deterministic sort: **O(N log N)**, no O(N²) pairwise comparisons. The 200-candidate test doubles as a sanity bound (runs in milliseconds).

## 12. REAL / MOCKED / STUBBED
- Comparison/ranking: **REAL**
- Delta + summary evidence: **REAL**
- E03 delegation (`evaluate_candidates`): **REAL**
- Boundary validation (finite, unique, non-empty): **REAL**
- Provenance chain: **REAL**
- Solver/candidate generation: **NOT IMPLEMENTED** (out of scope; candidates come from the caller / future solver phase)
- Monte Carlo robustness (§17.6/§30): **NOT IMPLEMENTED** (E04 accepts overrun_risk as E03 input; sampling belongs to the simulation phase)
- Backend adapter / FastAPI / persistence: **NOT IMPLEMENTED**
- LLM explanation: **NOT IMPLEMENTED** (deliberately; blueprint §21/§35 reserve that for a later optional layer consuming this structured evidence)

## 13. Known limitations
1. **Feasibility is the caller's gate** — E04 will rank an infeasible candidate if handed one; the documented contract is E01-gating before comparison (see §6).
2. **Tie-breaking is neutral identifier ordering** — the specification defines no domain tie-breaker; if product later wants e.g. lower-overrun preference on ties, that is a spec change to document (and would be added as an explicit, tested policy — not hidden).
3. **`plan_id` ↔ `candidate_id` duplication is possible** in the delegation path if callers use different identities across E03/E04; E04 does not silently merge them (they serve different layers: plan identity vs scenario identity).
4. **Scenario *branching*** (PRD §32 what-if state copies) is not implemented here — E04 compares evaluated candidates; state branching/isolation belongs to the simulation/state layer (E05+ per PRD §31/§33).

## 14. E05 boundary
E05 (and the simulation phase generally) may consume:
- `ScenarioComparison` / `RankedCandidate` as the deterministic comparison baseline, including `objective_delta_from_best` for "Plan B is worse by X" style evidence;
- `ScenarioCandidate` as the canonical "evaluated scenario" wrapper to attach simulation outputs (e.g. Monte Carlo P(overrun)) alongside;
- `ComparisonSummary.component_deltas` / `wins_despite` as structured input for recommendation evidence (blueprint §21 `alternatives` payload).

E05 must NOT expect from E04: scenario state branching/isolation, duration sampling, solvers, or any persistence. E04 deliberately does not touch live or scenario state.
