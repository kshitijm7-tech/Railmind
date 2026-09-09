# RailMind Railway Operational Data Foundation

> RailMind Operational Demo Dataset is synthetic scenario data created for
> demonstration, testing and optimization research. It does not represent
> live Indian Railways operational data.

## 1. Purpose

One coherent operational railway world — a single fictional corridor —
that the frontend, backend APIs, E09 CP-SAT planner, E05 simulation, P17
decision intelligence and P18 recovery all understand. No second
frontend-only dataset, no second engine-only train representation.

## 2. Architecture

```text
data/railway_demo/*.json            synthetic canonical dataset
        ↓
backend/app/infrastructure/railway_demo/
  loader.py                          dataset discovery + cached load
  repository.py                      OperationalRepository + DemoSeedRepository
  validate.py                        §15 consistency rules + counts
        ↓ (adapters: flat demo rows → existing domain contracts)
InMemory*Repository                  existing contracts, seeded from demo
        ↓
FastAPI domain APIs (/api/v1/...)    existing + new operational routes
        ↓
Frontend services/hooks/components   real-API with mock fallback
        ↓
E09 planner → E05 simulation → P17 intelligence → P18 recovery
```

Existing domain contracts (`app.domain.models.*`) were **not** changed.
The seed loader adapts demo rows to them:

| Demo value | Canonical contract |
| --- | --- |
| `PREMIUM_EXPRESS` / `SUPERFAST` | `TrainType.EXPRESS` |
| `ELECTRICAL` | `Department.OHE` |
| `SIGNALLING` (dept) | `Department.SIGNALING` |
| `SIGNALLING` (asset) | `AssetCategory.SIGNAL` |
| Flat train rows | Nested `Train{service, priority, ...}` (priority 1–4 preserved) |
| Demo windows/durations | `TimeInterval` / `DurationMinutes` |

Demo-only fields (headway, `section_type`, delays, routes, planning
windows, disruption scenarios) remain available in the raw rows via
`DemoSeedRepository` for engine use.

## 3. Dataset (corridor C-07 — Anandpur–Fatehgarh Main Line)

186.4 km double-line electrified, Demo Railway Zone / Central Division,
operational day 2026-09-10 (`Asia/Kolkata`).

| Entity | Count | IDs |
| --- | --- | --- |
| Stations | 6 | STN-A…STN-F (ANP/MGR/KDP/NRG/VPR/FGC) |
| Sections | 8 | SEC-01…05 main line, SEC-06 freight bypass, SEC-07 loop siding, SEC-08 goods loop |
| Trains | 12 | 2× P1 premium, 6× P2 express/superfast, 1× P3 passenger, 3× P4 freight |
| Train movements | 3 | MOV-001/002 occupied (SEC-03/SEC-02), MOV-003 completed |
| Assets | 5 | track / OHE / signalling / point machine |
| Maintenance tasks | 5 | TSK-001…005 (4 block-requiring, 1 non-block) |
| Disruptions | 2 | SCN-OVERRUN-01 (P18 demo), SCN-TRACK-FAIL-01 |

Note: the task brief listed 11 train rows under a "12 trains" heading;
`TRN-12431 Fatehgarh Superfast` was added as the twelfth so dataset, APIs
and docs agree.

Deliberate optimization pressure: premium vs freight priorities, shared
sections (SEC-02/SEC-03 used by 6+ trains), TSK-001 block on busy SEC-03
overlapping the morning bank, +6 min existing delay on TRN-12001,
SEC-06 freight-bypass routing choice, and a 45-minute overrun scenario.

## 4. Seed strategy

- `DemoSeedRepository` loads `data/railway_demo/` once per process
  (`lru_cache`) and exposes raw rows plus `domain_*()` adapted views.
- The three in-memory repositories seed from it at construction and fall
  back to legacy hardcoded rows only if the dataset is missing, so the
  app still boots in offline/mock mode and PostgreSQL is never required
  for the demo.
- Validation: `python scripts/validate_railway_demo.py` checks
  referential integrity, `entry < exit`, `earliest_start < latest_finish`
  and expected counts (6/8/12/3/5/5/2).

## 5. API endpoints

New (all demo-seed backed, paginated, filtered):

```text
GET /api/v1/stations[?is_junction=]          GET /api/v1/stations/{station_id}
GET /api/v1/sections[?corridor_id=&section_type=]
GET /api/v1/sections/{section_id}            (canonical alias of /track-sections)
GET /api/v1/train-movements[?train_id=&section_id=&status=]
GET /api/v1/disruptions[?section_id=&severity=&type=]
GET /api/v1/disruptions/{scenario_id}
GET /api/v1/corridor                         (C-07 metadata)
```

Extended (backward-compatible optional filters):

```text
GET /api/v1/trains?status=&train_type=&priority=
GET /api/v1/track-sections?corridor_id=
GET /api/v1/assets?section_id=
GET /api/v1/maintenance/tasks?section_id=&status=
```

## 6. Frontend integration

- `services/api/operationalApiService.ts` — typed real-API client for the
  new endpoints (stations, sections, movements, disruptions, corridor).
- `hooks/useOperationalData.ts` — one-shot parallel load for pages.
- `getNetwork()` now also fetches `/stations`, so the Command Center
  receives canonical names/codes/platforms/junction flags
  (`mappers.mapNetwork(..., stations?)`, registry optional).
- `RailwayNetworkSchematic` — same geometry, canonical bindings: station
  codes/names (ANP/MGR/KDP/NRG/VPR/FGC), junction flags (A/C/F),
  main-line slots SEC-01…05, SEC-06 freight-bypass arc, SEC-07 siding arc,
  186.4 km stat, train badges (12001→SEC-03, 12951→SEC-02, goods→bypass).
- `RailwayGanttTimeline` — canonical 8-section row list.
- No redesign of NetworkSchematic, Gantt, DetailModal,
  SimulationImpactDiagram or PlanComparisonVisualizer.

Remaining frontend-only copies (visual/test fixtures, not live paths):
`fixtures/demoCorridor.ts` (parallel mock corridor for unit tests),
`SimulationImpactDiagram` static cascade illustration.

## 7. Engine integration

- **E09 planner**: `PlanningService` reads tasks from the seeded
  maintenance repo and windows from the seeded operations repo, so
  `POST /api/v1/planning/generate` with `taskIds: [TSK-001, ...]`
  optimizes real demo tasks with real durations/windows. Generated plans
  reference `task_id`/`section_id` natively.
- **E05 simulation**: runs on generated plans unchanged
  (`POST /api/v1/simulations`); chain test uses `SCN-OVERRUN-01` as the
  scenario. Delay/occupancy/possession/conflict/throughput come from the
  existing simulation engine over canonical inputs.
- **P17 intelligence**: receives operational evidence (delays, priorities,
  occupancy, KPIs) through existing endpoints; `Insufficient Evidence`
  behavior preserved — nothing is fabricated.
- **P18 recovery**: `SCN-OVERRUN-01` (TSK-001 +45 min on SEC-03) is the
  primary demo flow: plan → block → overrun → conflict → impact →
  proposal-only recovery → re-planning. No auto-approval/execution.

## 8. Future real-data seam

```text
DemoSeedRepository
        ↓
OperationalRepository interface (stations/sections/trains/movements/
assets/tasks/disruptions/corridor)
        ↑
Future: IndianRailwaysDataAdapter / ExternalFeedAdapter /
        EnterpriseRailwayAdapter
```

No scraping, no external railway dependency for the SIH demo. Swap the
repository implementation later without touching contracts, engines or UI.

## 9. Verification

```bash
python scripts/validate_railway_demo.py
python -m pytest tests -q            # backend (from backend/)
python -m pytest tests -q            # engine (from engine/)
npm run typecheck && npm test && npm run lint && npm run build   # frontend
```

Current results: dataset validation OK; backend 169 passed (incl. 10 new
`test_railway_demo.py` incl. dataset→E09→E05 chain); engine 422 passed;
frontend typecheck/test (107)/lint/build green.
