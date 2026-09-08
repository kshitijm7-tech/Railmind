# RailMind Frontend Foundation (P01)

This is the P01 UI foundation for the Tier 1 RailMind modular monolith. It establishes the documented Next.js + TypeScript frontend shell, tokenized visual language, primary navigation, operational workspace layout, status indicators, and reusable decision card.

## Intentionally excluded

- No backend requests, persistence, authentication, or database layer
- No priority scoring, prediction, optimisation, simulation, recovery, or approval logic
- No fabricated operational data; UI placeholders identify the future API contract that will supply each value

## Run

```powershell
npm install
npm run dev
```

Use `npm run typecheck`, `npm run lint`, and `npm run build` for validation.

## F01 — API Integration

Flow: `Component -> Service (services/) -> API client (services/api/client/httpClient) -> FastAPI`.

- Configuration lives in `services/api/client/config.ts` and `.env.example`.
  Set `NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000`) and
  `NEXT_PUBLIC_API_MODE` (`auto` | `real` | `mock`, default `auto`).
  Never hard-code the base URL in services/components.
- Run with the real backend: start FastAPI on `:8000`, set
  `NEXT_PUBLIC_API_MODE=real` (or `auto`), then `npm run dev`. Browser
  `/api/v1/*` traffic is proxied via `next.config.ts` rewrites, so no
  backend CORS change is needed for local dev.
- Run with mocks (offline/demo): `NEXT_PUBLIC_API_MODE=mock npm run dev`.
- Integrated real endpoints: `GET /health`, `GET /version`, `GET /assets`,
  `GET /assets/:id`, `GET /track-sections`, `GET /track-sections/:id`,
  `GET /corridors`, `GET /corridors/:id`, `GET /maintenance/tasks`,
  `GET /maintenance/tasks/:id`, `GET /maintenance/defects`,
  `GET /maintenance/defects/:id`, `GET /trains`, `GET /trains/:id`,
  `GET /plans`, `GET /plans/:id`, `GET /plans/:id/versions`,
  `GET /plans/:id/metrics`, `POST /planning/generate` (202 + AsyncJob),
  `GET /planning/candidates` (backend stub, empty), `GET /planning/blocks`
  (backend stub, empty), `POST /plans/compare`, `GET /decisions`,
  `GET /decisions/:id`, `POST /decisions/:id/approve|reject|defer`.
- Mock-backed (no backend endpoint yet): simulations, disruptions/recovery,
  recommendations, audit events, global search, state metadata, task creation,
  generic decision submit. These stay behind the same service interfaces.
- Errors are normalized to `RailmindApiError` (`services/api/client/errors.ts`)
  with kinds for network/timeout/auth/validation/not-found/conflict/server and
  safe user messages (no stack traces/tokens in the UI).
- `hooks/useApiQuery.ts` provides `idle|loading|success|error` states with
  AbortController cancellation and stale-response guards.
- Contract notes: backend pagination is
  `{totalItems, page, pageSize, totalPages}` (frontend envelope differs —
  normalized in the client); backend `Train` wraps `service`; backend
  `ScheduledTiming.delayMinutes` / `Provenance.generatedAt` mix camelCase
  into an otherwise snake_case API (handled in `services/api/mappers.ts`).

### Required backend integration changes (not made in F01)

- Add CORS (`fastapi.middleware.cors.CORSMiddleware`) for the deployed
  frontend origin if production serves frontend/backend on different origins.
- Implement missing F02+ endpoints: simulations, disruptions, recovery,
  recommendations, audit events, jobs polling, state metadata, task creation.

## P02 handoff

The backend phase should define canonical state, entity, prediction, recommendation, scenario, plan, decision, event, alert, constraint, and impact contracts before this UI is connected. The decision card expects structured evidence for what, why, impact, risk, alternatives, and allowed human actions.
