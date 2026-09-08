# RAILMIND — E01 Implementation Report: Constraint & Rules Engine

**Phase:** E01 — Constraint Engine
**Agent:** Freebuff (Intelligence / Optimization / Simulation / ML Engine track)
**Branch:** `freebuff/engine`
**Status:** Implemented & Verified (88 engine tests + 27 backend tests passing)

---

## 1. Summary

E01 delivers the deterministic feasibility layer for RailMind: a pure-Python
`engine/` package that answers — for any candidate maintenance block and its
context — *"Is this operationally feasible under RailMind's documented
constraints?"* and *why*.

- 9 hard constraint rules (fail-closed on missing reference data)
- 4 soft constraint rules (PASS/WARNING only, never affect feasibility)
- Aggregated evaluation with explicit `feasible` semantics
- Fully explainable results (status, severity, message, explanation, typed evidence, violation degree)
- Versioned (engine, constraint set, per-rule) per the TRD reproducibility contract
- 88 unit tests incl. a hand-checkable 2-task / 2-window / 1-conflict fixture

No FastAPI, no SQLAlchemy, no network, no persistence, no clocks, no randomness.

## 2. Architecture

```
engine/models/inputs.py      pure input models (mirror canonical TS contracts)
engine/models/context.py     ConstraintContext (single evaluation input)
engine/constraints/base.py       ConstraintRule ABC (evaluate(context) → result)
engine/constraints/types.py      ConstraintType: HARD | SOFT (explicit enum)
engine/constraints/severity.py   INFO | WARNING | ERROR | CRITICAL
engine/constraints/result.py     ConstraintResult + ConstraintEvaluation
engine/constraints/_toolkit.py   shared helpers (interval math, evidence builders)
engine/constraints/hard/*.py     9 hard rules
engine/constraints/soft/*.py     4 soft rules
engine/constraints/engine.py     ConstraintEngine (aggregation, feasibility)
engine/tests/                    88 unit tests + hand-checkable fixtures
```

Dependency direction (enforced, verified by import scan):
`inputs → context → rules → engine → results`. The engine imports nothing
from `backend/`, `frontend/`, FastAPI, SQLAlchemy or any HTTP library.

## 3. Files Added

```
engine/__init__.py
engine/_version.py
engine/models/__init__.py
engine/models/inputs.py
engine/models/context.py
engine/constraints/__init__.py
engine/constraints/base.py
engine/constraints/configuration.py
engine/constraints/engine.py
engine/constraints/result.py
engine/constraints/severity.py
engine/constraints/types.py
engine/constraints/_toolkit.py
engine/constraints/hard/__init__.py
engine/constraints/hard/duration.py
engine/constraints/hard/operational_window.py
engine/constraints/hard/train_conflict.py
engine/constraints/hard/track_occupancy.py
engine/constraints/hard/resource_exclusivity.py
engine/constraints/hard/corridor_availability.py
engine/constraints/hard/planning_horizon.py
engine/constraints/hard/task_deadline.py
engine/constraints/hard/task_dependency.py
engine/constraints/soft/__init__.py
engine/constraints/soft/preferred_window.py
engine/constraints/soft/train_impact.py
engine/constraints/soft/workload_balance.py
engine/constraints/soft/resource_preference.py
engine/tests/__init__.py
engine/tests/conftest.py
engine/tests/helpers.py
engine/tests/fixtures/__init__.py
engine/tests/fixtures/hand_checkable.py
engine/tests/test_engine.py
engine/tests/test_duration.py
engine/tests/test_operational_window.py
engine/tests/test_train_conflict.py
engine/tests/test_track_occupancy.py
engine/tests/test_resource_exclusivity.py
engine/tests/test_corridor_availability.py
engine/tests/test_planning_horizon.py
engine/tests/test_deadline_dependency.py
engine/tests/test_soft_rules.py
```

## 4. Files Modified

None. The backend, frontend, contracts and docs are untouched. No existing
test, model or endpoint was changed.

## 5. Constraint Rules Implemented

### Hard
| Rule ID | Source | What it enforces |
|---|---|---|
| `RAILMIND.HARD.BLOCK_DURATION` | PRD §27.4, TRD §24.5, BP §17.4 c6 | Positive block duration; sum of assigned task expected durations fits (sequential in-possession model); block carries ≥1 task |
| `RAILMIND.HARD.OPERATIONAL_WINDOW_CONTAINMENT` | PRD §27.10, TRD §24.9, BP §17.4 c7 | Block contained in the section's operational window (inclusive boundaries); fail-closed if no window supplied |
| `RAILMIND.HARD.TRAIN_PATH_CONFLICT` | PRD §27.9, TRD §24.8 | No strict overlap between block and scheduled train-path segments on the block's section (adjacent allowed) |
| `RAILMIND.HARD.SECTION_EXCLUSIVITY` | PRD §27.8, TRD §24.2 | No overlap with existing exclusive occupancy of the same section (per-section, canonical IDs; adjacent allowed) |
| `RAILMIND.HARD.RESOURCE_EXCLUSIVITY` | PRD §27.6/27.7, TRD §24.3/24.4, BP §17.4 c4 | Department crew pool capacity (required + committed ≤ available, shift-window coverage) and explicit exclusive-pool double-booking; fail-closed on unmapped crewed departments |
| `RAILMIND.HARD.CORRIDOR_AVAILABILITY` | PRD §27.3, TRD §24.2 | Section not CLOSED; containing corridor available (canonical membership only); fail-closed on missing state |
| `RAILMIND.HARD.PLANNING_HORIZON` | PRD §27.10, TRD planning config | Block inside configured horizon (inclusive); explicit INFO pass when horizon is deliberately unconfigured |
| `RAILMIND.HARD.TASK_DEADLINE` | PRD §27.11, BP §17.4 c9 | Assigned tasks with mandatory `latest_finish` finish by their deadline (earliest deadline binding) |
| `RAILMIND.HARD.TASK_DEPENDENCY_PRECEDENCE` | PRD §27.5, TRD §24.6, BP §17.4 c8 | Predecessor blocks finish before dependent blocks start; unresolvable dependencies fail closed |

### Soft
| Rule ID | Source | What it prefers |
|---|---|---|
| `RAILMIND.SOFT.PREFERRED_WINDOW` | TRD §20, BP §12 night possessions | Block inside the preferred maintenance window (configurable hours, default 22:00–06:00) |
| `RAILMIND.SOFT.TRAIN_IMPACT` | TRD §20, BP §17.5 α | Temporal buffer from scheduled trains on the same section (configurable, default 15 min) |
| `RAILMIND.SOFT.WORKLOAD_BALANCE` | TRD §20 | Per-section maintenance load within tolerance of the cross-section average (configurable, default 25%) |
| `RAILMIND.SOFT.RESOURCE_PREFERENCE` | TRD §20 | Assigned tasks served by dedicated department resource pools |

## 6. Result Model

`ConstraintResult` — mirrors `frontend/contracts/planning/constraint.ts`
semantics (`constraint_id`/`is_satisfied`/`violation_degree`/`description`)
and extends them with identity + explainability fields:

```
rule_id · rule_version · constraint_type (HARD|SOFT) · status (PASS|FAIL|WARNING)
severity (INFO|WARNING|ERROR|CRITICAL) · message · explanation
affected_entities[] · evidence[] (source, description, quantity)
violation_degree (minutes or count of violation) · metadata
constraint_set_id · constraint_set_version · engine_version
is_satisfied  → True for PASS/WARNING (contract-compatible)
```

`ConstraintEvidence` = typed fact (source, description, optional quantity) —
blueprint §21 evidence discipline; no opaque scores.

## 7. Input Model

`ConstraintContext` (frozen Pydantic model, the single input object):

```
candidate_block       CandidateBlock (section_id, interval, task_ids, claimed resource pools)
tasks[]               TaskRequirement (department, duration estimate P-min/max, crew units, latest_finish, depends_on)
scheduled_tasks[]     ScheduledTaskRef (fixed layout for dependency checks)
train_paths[]         TrainPathRef (per-section segments)
operational_windows[] OperationalWindowRef (availability per section)
section_occupancies[] SectionOccupancy (existing exclusive use)
section_states[]      SectionState (OPEN/CLOSED/RESTRICTED)
corridors[]           CorridorState (canonical section membership + availability)
resource_pools[]      ResourcePool (department, units, shift window, exclusivity)
resource_demands[]    ResourceDemand (committed usage)
planning_horizon      TimeInterval | None
configuration         ConstraintEngineConfig (all business constants)
```

All datetime fields are validated timezone-aware at the model boundary —
naive datetimes are rejected before any comparison. Input model field names
deliberately mirror the canonical TS contracts (`TimeInterval`,
`DurationEstimate` ↔ `DurationMinutes`, `CandidateBlock` ↔ `Block`,
`TrainPathRef` ↔ `TrainPath`, `OperationalWindowRef` ↔ `OperationalWindow`,
`CorridorState` ↔ `Corridor`) so a backend adapter is a 1:1 mapping.

## 8. Versioning

- `ENGINE_VERSION = 0.1.0`
- `CONSTRAINT_SET_ID = "railmind-core-constraints"`, `CONSTRAINT_SET_VERSION = "1.0.0"`
- Every rule carries `rule_version = 1.0.0`
- Every `ConstraintResult` and `ConstraintEvaluation` is stamped with all three

This satisfies the TRD §67 reproducibility contract (future optimization runs
can record exactly which constraint definitions produced a verdict) without a
registry subsystem.

## 9. Explainability

Every result includes a one-sentence human-readable `message`, a full
`explanation` with the actual numbers (durations, deficits, overshoot
minutes, gap minutes), `affected_entities` (canonical identifiers —
`section:SEC-01`, `train:TRN-010`, `pool:POOL-ENG`, `task:TSK-101`),
structured `evidence` with quantities, and `violation_degree` for machines.
Example:

> FAIL / `RAILMIND.HARD.SECTION_EXCLUSIVITY` — "Section SEC-01 is already
> exclusively occupied during the proposed interval by 1 occupancy record(s)
> totalling 60.0 minutes of overlap." — evidence: `occupancy:OCC-900` (60.0).

## 10. Tests Added

88 tests across 9 files:

- **test_duration.py** (8): valid/zero/negative/exceeding, multi-task sums, empty block, naive-datetime rejection
- **test_operational_window.py** (8): inside, both boundaries, before/after, fail-closed, deterministic multi-window selection
- **test_train_conflict.py** (8): no overlap, partial, exact match, train-inside-block, block-inside-train, adjacency both sides, other-section, deterministic multi-train ordering
- **test_track_occupancy.py** (6): same-section overlap/adjacent, different-section, free, empty, sorted evidence
- **test_resource_exclusivity.py** (9): capacity pass/exceeded/deficit, shift-window coverage, fail-closed unmapped department, zero-crew, exclusive double-booking (both directions), adjacency, multi-pool
- **test_corridor_availability.py** (6): open/closed/restricted, corridor unavailable, non-membership, fail-closed
- **test_planning_horizon.py** (7): inside, both boundaries, before/after, outside, unconfigured
- **test_deadline_dependency.py** (10): deadline met/boundary/missed/earliest-binding/none; predecessor finished/violated/unscheduled/same-block/none
- **test_soft_rules.py** (12): preferred window inside/outside/partial/configurable; train impact none/near-miss/distant/overlap-delegation; workload balance/imbalance/no-data; resource preference mapped/unmapped/none
- **test_engine.py** (11): package hygiene, rule-set composition, forbidden-API scan, feasibility semantics (all-pass / hard-fail / soft-warning-only / multi-hard-fail), duplicate rule_id rejection, result-identity stamping, determinism, version stamps

## 11. Test Results

```
Engine:  python -m pytest engine/tests -q  →  88 passed in 0.14s
Backend: backend/.venv pytest -q           →  27 passed  (unchanged, no regression)
```

## 12. Typecheck / Lint / Build

The repository has no Python linter/type checker configured (noted in
onboarding). Per E01 §25 I did not introduce a tooling migration. A non-goal
scan confirms: engine imports only `pydantic` + stdlib; no
fastapi/sqlalchemy/httpx/urllib/socket anywhere under `engine/`; no
`datetime.now`/`random`/`uuid`/`time.time` in any rule module (enforced by a
unit test). Recommendation for a later phase: add `ruff` + `mypy` config at
repo root, applying to `engine/` and `backend/` together.

## 13. REAL / MOCKED / STUBBED

```
Constraint evaluation:            REAL (deterministic, tested)
Hard/soft rule logic:             REAL (9 hard + 4 soft, all unit-tested)
Input models:                     REAL (Pydantic, validated)
Feasibility aggregation:          REAL
Version stamping:                 REAL
Backend adapter (mapper):         NOT YET IMPLEMENTED (integration phase)
FastAPI endpoints:                NOT YET IMPLEMENTED (backend owner's phase)
CP-SAT consumption of results:    NOT YET IMPLEMENTED (E03)
Simulation scenario isolation:    NOT YET IMPLEMENTED (E04)
ML/LLM anything:                  NOT APPLICABLE (and must stay out per §12)
Database persistence:             NOT APPLICABLE
```

## 14. P07 Integration Boundary

P07's greedy planner and `ConflictDetector` are untouched. E01 establishes the
authoritative constraint layer; the intended seam (documented, not built):

```
P07 planner (temporary)  →  future integration  →  ConstraintEngine.evaluate(context)
                                                     ├── feasibility gate for generated candidates
                                                     └── evidence for PlanMetrics.constraints_violated
```

A backend adapter will map `backend/app/domain/models/*` + repos onto
`ConstraintContext` and surface `ConstraintEvaluation.feasible` /
`hard_failures` through the existing `ApiResponse` envelopes. That adapter
belongs to a coordinated integration phase (backend owner's boundary), not E01.

## 15. Known Limitations

1. **Intra-block task sequencing not evaluated.** If two tasks in one block
   depend on each other, ordering inside the block is accepted at E01 and
   deferred to E03's model (blueprint §17.4 c8 handles it as window-level
   precedence). Tested and documented.
2. **Scheduled-task refs carry no dependency metadata**, so only the
   predecessor direction is checkable (successor detection needs the full
   plan's dependency graph — future integration).
3. **RESTRICTED section status passes.** The canonical contracts define the
   enum but no restriction semantics; inventing any would violate the "no
   fabricated railway semantics" rule. Flagged as a contract gap.
4. **Corridor availability is engine-level.** Canonical `Corridor` has
   membership only; `CorridorState.is_available` is the smallest extension
   the documented constraint needs. Contract evolution requires multi-agent
   coordination per the workflow doc.
5. **Workload balance uses occupancy minutes** as the proxy for other
   sections' maintenance load; per-task scheduled durations don't exist in
   the context yet.
6. **Preferred-window semantics are wall-clock hours** in the context's own
   timezone; the canonical contracts carry no timezone metadata.

## 16. Antigravity Integration Requirements

For the future integration phase, the backend owner needs to:
1. Map repos → `ConstraintContext` (a pure function; the engine stays import-free of backend code, so the mapper lives in `backend/`).
2. Replace `PlanMetrics.constraints_violated` (currently a constant 0 in P07) with the count of hard FAILs.
3. Gate `PlanningService.generate_plan` candidates on `ConstraintEvaluation.feasible`.
4. Decide where `section_states` / `corridors` availability flags come from (contract gap §15.4).
5. Confirm the temporary P07 `ConflictDetector` is superseded by `RAILMIND.HARD.TRAIN_PATH_CONFLICT` at integration time.

## 17. Next Recommended Phase

**E02 — Priority Engine** (per the mandated sequence E01 → E02 → …). E01 is
genuinely complete: the feasibility layer is deterministic, explainable,
versioned and tested. E02 can consume `TaskRequirement` inputs directly and
feed its explainable priority scores into E03's objective weights
(blueprint §16.2 formula with configurable weights). CP-SAT (E03) should
consume `ConstraintEvaluation` + constraint-set versioning to build its hard
constraint set.

## 18. Git

```
Commit:  feat(engine): implement deterministic constraint engine (E01)
Branch:  freebuff/engine (tracks origin/freebuff/engine, no force-push)
Working tree: engine/ added; backend/, frontend/, contracts/, docs/ untouched
```
