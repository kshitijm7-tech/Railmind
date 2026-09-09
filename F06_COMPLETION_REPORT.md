# F06 Completion Report

## 1. Objective

Complete the Simulation & What-If Analysis workspace at `/simulation`: scenario branch
selection, governed simulation execution through the existing service interface, and
backend-faithful result presentation. No simulation algorithms, risk prediction, or
autonomous execution in the frontend — presentation and human review only.

## 2. Starting State (honest)

F06 began as an untracked draft (`frontend/app/simulation/SimulationWorkspace.tsx`) with
verified defects: 4 typecheck errors (branded `PlanId`/`ScenarioId`/`ScenarioContext`,
invalid `ButtonVariant "link"`), a 1-error lint failure (use-before-declare polling),
domain/contract result-shape mismatch (rendered `is_feasible`/`delayed_trains`/
`monte_carlo.p50` while the service returns the domain shape), dead button wiring
(`onClick={() => {}}`), and no route connection (`/simulation` rendered the older
scenario-branching page instead). The draft was rewritten, not patched.

## 3. Architecture

New/rewritten files:

- `frontend/hooks/useSimulationWorkspace.ts` — pure helpers: `buildRunRequest`
  (always carries an explicit `{ mode: 'SCENARIO', scenarioId }` boundary),
  `summarizeSimulation` (projection only), `selectDefaults` (first-available, never
  ranked), `hasUsableResult` (null-guard type predicate).
- `frontend/app/simulation/SimulationWorkspace.tsx` — rewritten against domain types:
  scenario branches, plan-under-test selection, wired run + bounded polling, domain-shape
  results, provenance badge.
- `frontend/app/simulation/page.tsx` — thin route wrapper (same pattern as F07).
- `frontend/tests/simulation-workspace.test.tsx` — 8 tests.

## 4. Preserved Behavior

The pre-existing scenario-branch cards (`enterScenario` via `OperationalContext`,
copy-on-write branching) are preserved inside the workspace's scenario section rather
than deleted — the old page's only capability survives alongside the new run flow.

## 5. Run Flow

Plan dropdown + scenario select → `Run Simulation` (disabled while running or when
either selection is missing) → `runSimulation` with governed request → bounded poll of
`getSimulationResult` (8 attempts × 1.5 s) → result panel, or an explicit
`result is not available yet` error with retry. Nothing is fabricated at any step;
`Dismiss` clears run state (no fake cancel endpoint is claimed).

## 6. Result Presentation (domain-faithful)

Renders exactly what `ISimulationService` returns: total delay, affected train/block
ids, maintenance completion %, Monte Carlo iterations / P(any violation) / expected
mean / P90, and backend `risk_level`. Copy states output is analytical evidence only
and never implies approval, with a link to the Decision Workspace.

## 7. Provenance / Errors / States

`Source: AUTO/REAL/MOCK` badge; `RailmindApiError` → `toUserMessage` (no stack traces);
`LoadingState` / `ErrorState` with retry / `EmptyState` for no-scenarios and no-plans.
Strict TypeScript throughout — zero `any` in new F06 code.

## 8. Navigation

`/simulation` route connected; links to `/planning` (generate plans), `/decisions`
(review evidence), `/` (command center). No `/comparison` link (that route does not
exist — same documented gap as F07).

## 9. Tests

8 tests: 4 helper (SCENARIO boundary shape, projection fidelity, defaults incl. empty,
null-guard) + 4 component (branches + plan select render; run carries SCENARIO boundary
and shows backend result; null-then-ready polling retries without fabricating; empty
plans state). Mocked services follow the established F07 test pattern.

## 10. Validation

- `npm test -- --run`: **103/103 pass (16 files)** — prior 95 + 8 new, zero regressions.
- `npm run typecheck`: **PASS**, zero errors (the 4 draft errors are gone by rewrite).
- `npm run lint`: **0 errors**; 11 remaining warnings are pre-existing in untouched
  `frontend/app/page.tsx`.
- `npm run build`: **PASS**, `/simulation` prerenders.
- Backend unreachable at build time (`BACKEND_UNREACHABLE` on `:8000/health`), so
  verification is mock-mode; live FastAPI verification remains open.

## 11. Files Changed

- `frontend/app/simulation/SimulationWorkspace.tsx` (rewritten)
- `frontend/app/simulation/page.tsx` (route wrapper)
- `frontend/hooks/useSimulationWorkspace.ts` (new)
- `frontend/tests/simulation-workspace.test.tsx` (new)
- `F06_COMPLETION_REPORT.md` (this file)

## 12. REAL / MOCKED / STUBBED / NOT IMPLEMENTED

- REAL: none verified (backend unreachable).
- MOCKED: scenario/plan/result flows (labelled via mode badge).
- NOT IMPLEMENTED (by design): simulation algorithms, risk computation, auto-run,
  cancellation endpoint, live backend verification.

## 13. Commit

`feat(frontend): build simulation workspace` on `opencode/frontend`.
