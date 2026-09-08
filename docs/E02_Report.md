# RAILMIND — E02 Implementation Report: Maintenance Priority Engine

**Phase:** E02 — Priority Engine
**Agent:** Freebuff (Intelligence / Optimization / Simulation / ML Engine track)
**Branch:** `freebuff/engine`
**Status:** Implemented & Verified (145 engine tests, 27 backend tests passing)

---

## 1. Purpose

E02 deterministically answers: *"How important is this maintenance requirement
relative to other maintenance requirements?"* It produces an explainable,
reproducible priority score and class per task, for consumption by E03
(optimize among feasible candidates) and display to humans (AC-001: tasks
must receive **explainable** priority scores). It explicitly does NOT answer
"when should this be scheduled" — that is E03.

## 2. Architecture

```
Canonical task vocabulary (TS contracts / blueprint §11.2)
        │  (adapter mapping, engine stays import-free of consumers)
        ▼
PriorityInput (frozen Pydantic)
        ▼
PriorityEngine ── PriorityEngineConfig (weights, maps, thresholds, policy)
        │
   factor normalization (bounded [0,1], explicit mappings)
        ▼
weighted mean → PriorityResult (score, class, factor_scores[], evidence)
        ▼
E03 objective input
```

Package: `engine/priority/` — `configuration.py`, `missing_data.py`,
`inputs.py`, `factors.py`, `engine.py`, `result.py`. Same discipline as E01:
no FastAPI/SQLAlchemy/HTTP/persistence, no clocks/randomness (verified by
scan), immutable inputs, config-driven constants.

## 3. Files Added

```
engine/priority/__init__.py
engine/priority/configuration.py
engine/priority/missing_data.py
engine/priority/inputs.py
engine/priority/factors.py
engine/priority/engine.py
engine/priority/result.py
engine/tests/test_priority_config.py
engine/tests/test_priority_factors.py
engine/tests/test_priority_engine.py
engine/tests/test_priority_contract.py
docs/E02_Report.md
```

## 4. Files Modified

- `engine/_version.py` — added `PRIORITY_MODEL_ID` / `PRIORITY_MODEL_VERSION`
- `engine/__init__.py` — re-exports the E02 public API
- Nothing else; backend/frontend/contracts untouched.

## 5. Priority Factors

Exactly the five factors mandated by **PRD FR-MI-001** (mirrored by blueprint
§16.2) — no more, no fewer:

| Factor | Input | Normalization |
|---|---|---|
| Criticality (30%) | canonical `Criticality` enum | explicit map: LOW .25 / MEDIUM .50 / HIGH .75 / CRITICAL 1.0 |
| Overdue days (20%) | `overdue_days` (required; "0 if not overdue" §11.2) | linear saturation, 0d→0.0, 30d→1.0 (configurable) |
| Asset failure risk (20%) | `AssetFailureRisk` (mirrors TS `FailureRiskPrediction`; optional) | probability itself ∈ [0,1] |
| Safety relevance (20%) | explicit flag, else task-type prior (optional) | flag → 1.0/0.0; type prior × share (EMERGENCY 1.0, CORRECTIVE/DEFECT .75, INSPECTION .25, PREVENTIVE 0) × 0.5 |
| Downstream impact (10%) | `trains_per_day` on the section (optional) | linear saturation, 60 trains/day → 1.0 (configurable) |

Deliberately absent: a separate deadline factor. The spec carries time
pressure through `overdue_days`; deadline-vs-evaluation-time pressure would be
an invented factor. `PriorityInput.evaluation_time` exists (tz-aware,
validated) for future time-sensitive factors without schema change.

## 6. Scoring Model

```
score = Σ (normalized_factor_i × normalized_weight_i)   ∈ [0, 1]
```

- Configured weights are renormalised to Σ=1 when they don't sum to 1
  (explicit, reported via `metadata.weights_renormalized`).
- All-zero weights are rejected at the configuration boundary — never a
  misleading score.
- Score, contribution total and exposed weights reconcile within 1e-9
  (mathematically tested with independent recomputation).

## 7. Normalization

Deterministic, bounded, documented, monotonic. Enum→score maps and saturation
points live in `PriorityEngineConfig` (no magic numbers in factor code).
Unknown enum values in *configuration* raise immediately (missing map entry is
a config error, not a data gap).

## 8. Weight Configuration

Defaults are the authoritative FR-MI-001 values (0.30/0.20/0.20/0.20/0.10),
marked [ASSUMPTION] by the blueprint and exposed for tuning. Validation:
`weight >= 0` (pydantic), not-all-zero (engine + config), strict threshold
ordering, positive saturation bounds.

## 9. Priority Classification

Canonical enum `LOW | MEDIUM | HIGH | CRITICAL` with configurable thresholds
(default 0.40 / 0.65 / 0.85). Boundary ownership explicit: `>=` — a score
exactly on a threshold belongs to the higher class. Every class and every
boundary is tested; thresholds must be strictly increasing (validated).

## 10. Deadline Handling

Time pressure = overdue-days factor (spec-mandated). Monotone in overdue
days, saturating at the configured bound (30d default). No `datetime.now()`
anywhere; evaluation_time is explicit input only. Tests: far (0d) / near (5d)
/ saturated (≥30d) ordering.

## 11. Missing Data Policy

- **Required, fail-closed:** `criticality`, `overdue_days`, `task_id`,
  `section_id` — absence is a construction `ValidationError`; unknown enum
  values rejected (safety-critical inputs are never guessed).
- **Optional factors** (`failure_risk`, `safety` without flag/type,
  `downstream_impact`): configurable policy —
  - `EXCLUDE_FACTOR` (default): factor omitted, weights renormalised over
    present factors, reported in `missing_factors` + explanation + evidence;
  - `ZERO`: factor scores 0.0 with retained weight, reported in explanation.

## 12. Explainability

`PriorityResult.explanation` names the task, class and score, then lists each
contributing factor with raw value, normalized score, weight and contribution
(two-decimal stable formatting), zero-weight factors, and missing-factor
policy notes. `factor_scores[]` carries the full calculation;
`contributing_factors()` ranks by contribution (deterministic tie-break).
Evidence lines record provenance per value (`canonical:Criticality`,
`config:safety_task_type_scores`, `risk-model:<id>@<ver>` or
`deterministic-baseline`). Example:

> Task TSK-101 classified CRITICAL with priority score 0.91 — driven by:
> criticality (criticality=CRITICAL, normalized 1.00, weight 0.30,
> contribution 0.30); overdue (3 day(s) overdue …, normalized 0.10, …) …

## 13. Versioning / Provenance

`engine_version=0.1.0`, `priority_model_id=railmind-deterministic-priority`,
`priority_model_version=1.0.0` stamped on every result. Metadata records
`constraint_set_id/version` (E01 lineage), renormalisation flag, section and
asset ids. The safety/risk factor provenance distinguishes model-supplied vs
deterministic-baseline values — the TRD §16 deterministic-fallback principle.

## 14. E01 Relationship

Zero coupling. E02 shares only the package namespace, the `ENGINE_VERSION`
constant and E01's discipline (tz-aware validation helper imported from
`engine.models.inputs`). E01 gates *feasibility*; E02 ranks *importance*;
neither requires the other at runtime. Independent test suites confirm.

## 15. E03 Integration Boundary

E03 consumes per-task: `score` (→ priority weight β·priority_t in BP §17.5),
`priority_class` (grouping/policy), `factor_scores[].contribution` (objective
breakdown/explainability). The result is a frozen Pydantic model — directly
serialisable into an optimizer's input payload. No solver, no OR-Tools touched.

## 16. Tests Added

57 new tests (total engine suite 145):

- **config (9):** PRD defaults, negative/all-zero weights rejected at boundary, renormalisation, threshold ordering, saturation positivity, policy default
- **factors (17):** explicit enum map + monotonicity + missing-map config error; overdue minimum/intermediate/saturation/cap/configurable; risk bounds/provenance/absent; safety flag-dominance/override/monotone priors/scaled share/absent; downstream boundaries/absent
- **engine (24):** independent score recomputation (§20), contribution reconciliation, weights sum to 1, renormalisation-to-mean, every class + every boundary (§19), maximal/minimal inputs, configurable thresholds, weight-change effects, zero-weight reporting, EXCLUDE vs ZERO policies (reporting + math), required-factor fail-closed, unknown criticality, overdue time-pressure ordering + saturation, identical-input identity, score bounds, single-factor monotonicity, explanation completeness (§13), ranked contributions, version stamps
- **contract (4):** frontend §12-dataset fixture vocabulary (incl. blueprint "Defect" type), backend `MaintenanceTask` attribute surface with documented gaps, cross-task comparability (AC-001)

## 17. Test Results

```
Engine:  145 passed in 0.24s   (57 new E02 tests + 88 E01 tests)
Backend: 27 passed             (unchanged — no regression)
Hygiene: no fastapi/sqlalchemy/httpx/requests/socket/urllib; no
         datetime.now/utcnow/time.time/random/uuid in engine/priority
```

## 18. Typecheck / Lint / Build

Repository has no Python linter/type checker (unchanged decision from E01;
not introducing a tooling migration for E02). Quality enforced through:
pydantic validation boundaries, hygiene scans, determinism tests.

## 19. REAL / MOCKED / STUBBED

```
Priority calculation:      REAL (deterministic weighted model, FR-MI-001)
Normalization:             REAL (explicit maps/saturation, tested)
Classification:            REAL (explicit thresholds, tested)
Explainability:            REAL (full factor decomposition, tested)
Missing-data policy:       REAL (two policies, tested)
Backend adapter:           NOT IMPLEMENTED (mapping shown in tests; integration phase)
FastAPI integration:       NOT IMPLEMENTED
ML priority model:         NOT IMPLEMENTED (deterministic baseline is the
                           TRD-mandated fallback and is what ships; an ML
                           variant behind the same interface is future work)
LLM:                       NOT IMPLEMENTED (and out of scope by architecture)
E03 optimizer:             NOT IMPLEMENTED
```

## 20. Known Limitations

1. **Two canonical task-type vocabularies coexist** (TS enum
   PREVENTIVE|CORRECTIVE|INSPECTION|EMERGENCY vs blueprint §11.2
   Preventive|Corrective|Inspection|Defect). The engine accepts the union
   (case-insensitive, DEFECT mapped corrective-like) — contract convergence
   requires multi-agent coordination.
2. **`trains_per_day` has no canonical source** (TrackSection carries no
   traffic volume) — must be supplied by the caller/adapter.
3. **Safety task-type priors are configurable assumptions** (flagged
   [ASSUMPTION]); an explicit `is_safety_relevant` flag always dominates.
4. **Failure-risk input is caller-supplied**; E06 will produce it. The input
   already carries model provenance fields for that handoff.
5. **No safety-floor rule** — inspected TRD/PRD/blueprint governance
   sections; none mandates forcing a minimum class for safety-critical
   conditions, so none was invented (E02 §16). Flagged for domain review.
6. **Section/asset criticality context** (`AssetContext`, `SectionContext`)
   is defined but not yet a factor input path — the spec's criticality factor
   is task-level; asset-level criticality enters via E06's risk model.

## 21. Cross-Agent Integration Requirements

1. **Antigravity (backend):** expose `overdue_days` and section
   `trains_per_day` in the backend task/section domain (both required by
   FR-MI-001 but absent from backend models today); map `MaintenanceTask` →
   `PriorityInput` at integration time; surface `PriorityResult` through
   `/api/v1/maintenance/prioritize` (PRD §60 already names this endpoint).
2. **OpenCode (frontend):** `PriorityBreakdown` in the TS contract uses
   safety/reliability/efficiency/total — different axes than FR-MI-001's
   factors; decide whether the contract evolves toward
   factor_scores[] or the frontend renders the engine's factor list as-is.
3. **Contract owners:** converge the two task-type vocabularies (§20.1).

## 22. Git

```
Commit:  feat(engine): implement deterministic priority engine (E02)
Branch:  freebuff/engine (not pushed — awaiting instruction)
Working tree: engine/priority/ added; engine/__init__.py + engine/_version.py
              modified; docs/E02_Report.md added; nothing unrelated touched
```
