# F05/F07 Route & Live Integration Verification

## 1. Baseline

- Commit: `6e5b138` (branch `opencode/frontend`, clean tree, in sync with origin).
- Tests: **103/103 passing (16 files)** — verified, not assumed.
- Typecheck: clean. Lint: 0 errors, 11 pre-existing warnings (`app/page.tsx`, untouched).
- Build: passing (12 routes).
- Backend at start of work: unreachable (`BACKEND_UNREACHABLE` on `:8000/health`).

## 2. Task 1 — `/comparison`

- Files changed:
  - `frontend/app/comparison/page.tsx` (new) — thin wrapper rendering the existing
    default-exported `PlanComparisonWorkspace`. No logic duplicated, F05 untouched.
  - `frontend/config/workspaceConfig.ts` — added `/comparison` title/eyebrow entry
    (existing AppShell title mechanism).
  - `frontend/components/layout/Sidebar.tsx` — added `Plan Comparison → /comparison`
    item in the PLANNING group between Block Planning and Simulation (existing
    navigation mechanism; distinct 📊 icon).
- Navigation verified: flow is now Command Center → Planning → **Comparison** →
  Simulation → Decisions through the sidebar in flow order. F04's in-page
  "Compare Plans" button behavior intentionally unchanged (still calls the compare
  service directly; not redesigned). F06/F07 link to `/planning` and `/simulation`;
  no dead comparison links existed or were added.
- Route rendering verified: production build prerenders `/comparison` (13 pages,
  previously 12).

## 3. Task 2 — `deferUntil`

- Contract status (current source of truth, both sides support it):
  - Frontend `DeferDecisionBody.deferUntil?: ISOTimestamp`
    (`contracts/api/decision/requests.ts:29-33`).
  - Backend `DeferDecisionBody.deferUntil: Optional[datetime] = None`
    (`backend/app/domain/models/decision.py:35-39`); service appends
    `(Deferred until …)` to the audit record; backend pytest posts
    `"deferUntil": "2026-10-01T00:00:00Z"`.
  - `ApiDecisionService.deferDecision` already forwards the field — no service change.
- UI change (minimal, existing design kept): optional `datetime-local` input
  `f07-defer-until`, rendered **only inside the confirm dialog for the defer action**;
  new `toDeferUntilIso` helper normalizes to UTC ISO (`ISOTimestamp`) or `null`
  when empty/invalid; invalid input blocks submit with a safe message; value omitted
  from payload when empty; cleared on success, preserved on error.
- Tests: helper test (UTC normalization, empty/invalid → null) + component test
  (defer payload carries `deferUntil` through the existing service; success recorded).

## 4. Task 3 — Live Backend

Backend started with the repo's own stack, unmodified: `python -m uvicorn
app.main:app --host 127.0.0.1 --port 8000` (FastAPI/uvicorn per
`backend/requirements.txt`; in-memory repos, no migrations/seeds needed).
Verification used the exact request shapes the frontend sends (including F04's
generate body). Servers were restarted between decision phases to restore the
seeded PENDING decision; no backend code was changed and no stray processes remain.

| Capability | Endpoint/Flow | Status | Evidence | Notes |
| ---------- | ------------- | ------ | -------- | ----- |
| Planning list/detail | `GET /plans`, `GET /plans/PLAN-001` (+`/versions`, `/metrics`) | REAL | 200, seeded PLAN-001 with blocks/metrics/version/provenance | Missing id → 200 + `data:null`, handled by `getPlanById` |
| Planning generation | `POST /planning/generate` → 202 `AsyncJob` → followed `resultEndpoint` | REAL | `JOB-81566467` COMPLETED → real `PLAN-c89407` (DRAFT, BALANCED) | F04's exact body accepted (`strategy:'BALANCED'`, `scenarioContext:'LIVE'`) |
| Candidates/blocks | `GET /planning/candidates`, `GET /planning/blocks` | STUBBED | 200 + `data:[]` | Frontend documents this; mock fallback covers UI |
| Comparison | `POST /plans/compare` | REAL | 200, candidates with metrics, `recommendationRank:1`, `recommendedPlanId`, tradeoffSummary | — |
| Simulation | (no backend endpoints; zero `simulat*` matches in `backend/app`) | MOCKED | `serviceFactory` hardwires `mocks.simulation` even in real mode | Never claimed live; F06 UI labels mock mode |
| Approve | `POST /decisions/DEC-001/approve` | REAL | 200 → `APPROVED`, approval record, `audit_history:[AUDIT-…]`, re-read confirms | — |
| Reject | `POST /decisions/DEC-001/reject` (fresh boot) | REAL | 200 → `REJECTED`, justification + audit entry, re-read confirms | — |
| Defer | `POST /decisions/DEC-001/defer` + `deferUntil` (fresh boot) | REAL | 200 → `DEFERRED`, justification + audit entry; `deferUntil` accepted, embedded in server audit detail | — |
| Decision errors | re-approve terminal; `GET /decisions/DEC-NOPE` | REAL | Terminal re-action → HTTP 200 + `{data:null,error:{…400}}`; missing → real 404 → NOT_FOUND mapping | See §5 limitation |

## 5. Domain Mapping Findings

Verified (backend payload → mapper → domain): `mapPlan` (ids, `BALANCED`→`Balanced`,
`APPROVED`→`Approved`, `interval/tasks`, `total_train_delay_minutes:20.5`,
`overall_score:95`, `version.created_at`) — all fields present, no fallbacks
triggered. `mapDecision` (`target_plan_id`→`plan_id`, `Plan Approved`+`APPROVED`→
`APPROVE`, approver/role round-trip, justification→notes). `mapAsyncJob`
(jobId/COMPLETED/timestamps/`resultEndpoint`).

Bugs found (documented, NOT fixed — fixes require changes this task forbids):
1. `IPlanningService.comparePlans` returns `Plan[]`: the service extracts planIds
   from the backend's rich `ComparePlansResponse` and re-fetches plans, **discarding
   `recommendationRank`/`constraintViolations`/`overrunRisk`**. F05 therefore shows
   rank 0/neutral. Fixing needs an interface change + F05 rewrite (explicitly forbidden).
2. Terminal-state re-actions return HTTP 200 + `{data:null, error:{…400}}`; the
   frontend raises generic MALFORMED instead of surfacing "not in PENDING state".
   Safe (error shown, no false success) but lossy; fixing needs error-strategy redesign.

Remaining mismatches: none functional. Backend `Provenance.state: MOCKED` on seed data
is backend-labelled demo data, surfaced as-is.

## 6. Validation

- Tests: before **103/103** → added **2** → after **105/105 (16 files)**.
- Typecheck: clean. Lint: 0 errors (same 11 pre-existing warnings).
- Build: passing, 13/13 routes including `/comparison`.

## 7. Remaining Limitations

1. Live verification ran against seeded in-memory state (fresh boots per phase);
   no persistent DB to verify against.
2. Simulation has no backend endpoints at all — MOCKED by architecture, not by gap.
3. §5 items 1–2 intentionally left open per scope protection.
4. `GET /plans/:id` for a missing plan returns 200+null rather than 404 (backend).

## 8. Final Status

- F05 route gap: **CLOSED** (`/comparison` live, sidebar + config + build verified).
- F07 deferUntil gap: **CLOSED** (contract-supported, UI + service payload + tests).
- Live backend verification: **COMPLETE** for planning/comparison/decisions
  (approve/reject/defer incl. `deferUntil`); simulation correctly classified MOCKED.
