# F07 Completion Report

## 1. Objective

Build a production-grade Decision Workspace at `/decisions` where an authorized human reviews
planning evidence and records a governed Approve / Reject / Defer decision. The frontend must
never decide autonomously; the backend remains authoritative for governance, state transitions,
and audit persistence.

## 2. Pre-Implementation Repository Assessment

Branch: `opencode/frontend` (up to date with `origin/opencode/frontend`).
Baseline commit: `9044e65 feat(frontend): build maintenance workspace`.
Working tree before F07 contained uncommitted F04/F05 work plus an untracked F06 draft:

- `M frontend/app/planning/page.tsx`, `?? frontend/app/comparison/`,
  `?? frontend/app/simulation/SimulationWorkspace.tsx` (left untouched except one
  compile-compatibility shim — see §3).
- Existing `/decisions` page submitted decisions through the legacy `submitDecision` shim
  with a hardcoded approver and `alert()` feedback — no rationale input, no confirmation,
  no reject/defer path, no conflict handling.
- Canonical contracts used: `contracts/decision/decision.ts` (DecisionStatus),
  `contracts/api/decision/requests.ts` (Approve/Reject/Defer bodies),
  `contracts/api/decision/responses.ts`, `domain/types/decisions.ts` (DecisionRecord),
  `domain/types/recommendations.ts` (Recommendation), `services/types.ts`
  (IDecisionService), `services/api/decisionApiService.ts`,
  `services/api/client/errors.ts` (RailmindApiError).
- Baseline test run before F07: **85/85 passing across 14 files** (recorded, not assumed).

## 3. F06 Dependency Status — INCOMPLETE (unchanged)

F06 is **INCOMPLETE**. Verified in the working tree:

- `frontend/app/simulation/SimulationWorkspace.tsx` is untracked, unrouted
  (`/simulation` still renders the old scenario-branching page), has dead button wiring
  (`onClick={() => {}}`), renders contract-shape result fields while the service returns
  the domain shape, and has no tests or completion report.
- F07 consumes simulation **only** through the existing valid interface
  `ISimulationService.getSimulationResult()` wrapped in try/catch. A null/throwing result
  renders `Simulation evidence not available`. No fake simulation data is ever created.
- Smallest-compatibility change (working tree only, NOT committed, NOT an F06 repair):
  added branded-type casts and `variant "link" → "ghost"` so the F06 draft compiles and
  `npm run build` can validate F07. F06's functional gaps (wiring, routing, tests) remain
  exactly as found. F07's commit contains no F06 files.

## 4. Decision Workspace Architecture

New files (all F07):

- `frontend/hooks/useDecisionWorkspace.ts` — pure, unit-tested helpers:
  `canActOnRecommendation`, `validateDecisionInput`, `summarizeConstraints`,
  `buildDecisionQueue`, `hasSimulationEvidence`, `findCandidatePlan`.
- `frontend/app/decisions/DecisionWorkspace.tsx` — evidence sections + governed actions.
- `frontend/app/decisions/page.tsx` — thin route wrapper rendering the workspace.
- `frontend/tests/decision-workspace.test.tsx` — 10 tests.

Data flow: recommendations + plans + decision history load in parallel; candidate plan
resolves from the plan list (fallback `getPlanById`); simulation loads best-effort;
actions go through `IDecisionService.approve/reject/deferDecision`; history is
re-fetched from the backend after every confirmed action.

## 5. Decision Queue

`buildDecisionQueue` composes the pending backend recommendation
(`PENDING_REVIEW`/`APPROVED`/`MODIFIED`/`REJECTED` — contract states only) with
`DecisionRecord` history (`APPROVE`/`MODIFY`/`REJECT`). Selecting an entry switches the
detail pane; recorded entries are shown as immutable with an audit-trail pointer.

## 6. Decision Detail

Header (recommendation id / status / candidate plan / state version), decision context
(action summary + primary rationale + evidence-hierarchy note), candidate plan,
alternatives, constraint evidence, simulation evidence, risk, rationale, actions,
history — matching the spec layout, adapted to `SectionCard`/`AppShell` conventions.

## 7. Candidate Plan Evidence

Plan id, name, status, strategy, total delay, maintenance cleared, overrun risk, and
provenance (`REAL`/`MOCK`/`AUTO` mode label). Resolved via existing planning service;
missing data renders `Supporting evidence is not available.` Links to `/planning`.
No comparison logic duplicated.

## 8. Alternative Plans

Renders `recommendation.alternatives` verbatim (backend-provided deltas and ranks only).
Explicit copy states the frontend does not rank. Note: the F05 comparison workspace
component exists but has **no route** (`/comparison` 404s — no `app/comparison/page.tsx`),
so F07 links plan evidence to `/planning` instead of a dead comparison link.

## 9. Constraint Evidence

Renders the backend `constraint_trace` (category + `SATISFIED`/`TIGHT`/`VIOLATED`/
`RELAXED`) as-is. Any `VIOLATED` item triggers a prominent `role="alert"` banner
(`HARD CONSTRAINT VIOLATION — N violated of M traced`), never styled as a mild warning.
No HARD/SOFT labels are invented — the backend contract carries no such field.

## 10. Simulation Evidence

Domain-shape result (`scenario_id`, total delay, affected trains, completion rate,
risk level) when the service returns one; otherwise `Simulation evidence not available`
with an explicit F06-incomplete note and a `/simulation` link. Copy states simulation
is analytical and never implies approval.

## 11. Risk Evidence

Displays backend-provided values only (`expected_outcome.overrun_risk_pct` and plan
`overall_overrun_risk`). No frontend computation or inference. Copy states this.

## 12. Human Rationale

Approver name (required), role selector (the three contract `UserRole` values), and a
free-text rationale (required for all three actions: approve → justification,
reject/defer → reason, per `ApproveDecisionBody`/`RejectDecisionBody`/
`DeferDecisionBody`).

## 13. Approve Workflow

Validate → `Confirm Approve?` dialog (ids, candidate, "recorded in decision history",
"plan is not executed") → submit → backend response → history refresh → confirmation
(`recorded as DEC-… via MODE service` + audit link). Rationale preserved during
submission, cleared only on success. Buttons disabled while submitting.

## 14. Reject Workflow

Same two-step pattern with `danger` confirm styling. Reason required before the dialog
opens. Accidental rejection impossible (explicit confirm required).

## 15. Defer Workflow

Supported via `deferDecision` (contract body). Recorded as a distinct deferred outcome;
copy never conflates defer with reject.

## 16. Decision State Machine

`canActOnRecommendation` enables actions only for `PENDING_REVIEW`. Any other status
disables all three buttons with an explanatory note. No frontend state machine is
hardcoded beyond this contract-derived gate; transitions come from backend responses.

## 17. Concurrency / Conflict Handling

`CONFLICT` (`409`) from `RailmindApiError` produces a safe message naming possible
another-user action, refreshes history (best-effort), and keeps the rationale for review.
Backend state is never overwritten; state is re-read, never assumed.

## 18. Audit Integration

No duplicate audit system. History section plus `Open audit trail` links to the existing
`/audit` route. Success messages point at the audit trail; persistence is claimed only
as "recorded" after a backend response.

## 19. Provenance

`Source: AUTO/REAL/MOCK` badge from `getConfiguredApiMode()` on the workspace header,
per-plan provenance, and per-action provenance in confirmations
(`via MODE service`). Mock data can never look real.

## 20. Loading / Error / Empty States

`IDLE/LOADING/SUBMITTING/SUCCESS/ERROR` covered: `LoadingState` for queue load,
`ErrorState` with retry, `No decisions currently require review.`,
`This decision could not be loaded.`, `Supporting evidence is not available.`,
`Simulation evidence not available`. Unavailable data is distinguished from empty data.

## 21. Navigation Integration

Command Center → `/decisions` (existing sidebar/alert links untouched); Decision →
`/planning` (plan), `/simulation` (evidence, graceful), `/audit` (trail), `/` (command
center). Comparison deep-link omitted deliberately (§8).

## 22. Accessibility / Responsive Design

Semantic headings, labelled inputs (`htmlFor`), `aria-pressed` queue buttons,
`role="dialog" aria-modal` confirmation, `role="alert"`/`role="status"` messaging,
text-plus-color statuses, keyboard-operable native controls, wrapping flex layouts and
auto-fit grids that collapse on narrow screens.

## 23. API Integration

Uses `IDecisionService` exactly (`approveDecision`, `rejectDecision`, `deferDecision`,
`getDecisionHistory`) with contract bodies; errors via `RailmindApiError` +
`toUserMessage` (no stack traces). Backend was unreachable during implementation
(`http://localhost:8000/health` → `BACKEND_UNREACHABLE`), so verification is mock-mode
via `MockDecisionService`; live verification remains open.

## 24. Tests

`frontend/tests/decision-workspace.test.tsx` — 10 tests: 6 helper (gating, validation,
constraint summary, queue composition, simulation-null, candidate lookup) and 4
component (render + graceful simulation-empty + navigation links; validation blocks
submit with zero backend calls; confirmation gate before backend call + success record;
non-pending status disables actions).

## 25. Validation

- `npm test -- --run`: **95/95 pass (15 files)** — baseline 85 + 10 new, zero regressions.
- `npm run typecheck`: **PASS** (clean; required the §3 F06 compile shim in working tree).
- `npm run lint`: F07 files clean; 1 remaining error is the pre-existing F06
  declaration-order issue + 12 pre-existing `app/page.tsx` warnings. Untouched by design.
- `npm run build`: **PASS** — all routes prerender including `/decisions`.
- Backend decision endpoints: not verified live (backend unreachable); mock-verified only.

## 26. Files Changed

- `frontend/app/decisions/DecisionWorkspace.tsx` (new, ~420 lines)
- `frontend/app/decisions/page.tsx` (rewritten as route wrapper)
- `frontend/hooks/useDecisionWorkspace.ts` (new)
- `frontend/tests/decision-workspace.test.tsx` (new, 10 tests)
- `F07_COMPLETION_REPORT.md` (this file)
- Working-tree-only, NOT committed: 3-line compile shim in untracked
  `frontend/app/simulation/SimulationWorkspace.tsx` (§3).

## 27. Backend Dependencies

Requires `GET /decisions`, `POST /decisions/:id/approve|reject|defer` per
`decisionApiService.ts`; recommendation, planning, and simulation reads per existing
services. No backend changes made. Live-backend confirmation of the three action
endpoints is still owed when the FastAPI service is available.

## 28. Known Limitations

1. F06 INCOMPLETE — simulation evidence path exercised against mock/domain shape only.
2. No `/comparison` route exists, so alternative→comparison navigation is a documented gap.
3. Defer maps to a `MODIFY` action record in the mock service (mock limitation).
4. Live backend verification pending (service unreachable at build time).
5. Lint still reports the pre-existing F06 error + `app/page.tsx` warnings.

## 29. REAL / MOCKED / STUBBED / NOT IMPLEMENTED

- REAL: none verified (backend unreachable).
- MOCKED: queue, candidate, simulation, and action flows (mock services, labelled).
- STUBBED: nothing new.
- NOT IMPLEMENTED: auto-approval/execution (forbidden by design), frontend risk
  scoring, comparison deep-link (no route), live endpoint verification.

## 30. Regression Status

Baseline before F07: **85/85 (14 files)**. F07 adds 10 tests. Final: **95/95
(15 files)**. No pre-existing failures; no regressions. Typecheck/lint deltas are
limited to the documented pre-existing F06 items.

## 31. Commit

`feat(frontend): build decision workspace` on `opencode/frontend`, pushed to
`origin/opencode/frontend`. Staged scope is F07 files + this report only; F04/F05/F06
working-tree items were deliberately left uncommitted.

## 32. Next Recommended Phase

1. Bring FastAPI up and live-verify approve/reject/defer + conflict paths.
2. Complete or formally scope-cut F06 (wire, route, domain/contract alignment, tests).
3. Add the missing `/comparison` route so F07 alternatives can deep-link (F05).
4. Consider defer-until date input (contract supports `deferUntil`; UI omits it).
