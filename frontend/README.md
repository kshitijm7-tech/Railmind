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

## P02 handoff

The backend phase should define canonical state, entity, prediction, recommendation, scenario, plan, decision, event, alert, constraint, and impact contracts before this UI is connected. The decision card expects structured evidence for what, why, impact, risk, alternatives, and allowed human actions.
