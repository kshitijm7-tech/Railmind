# RailMind Operational Demo Dataset

> RailMind Operational Demo Dataset is synthetic scenario data created for
> demonstration, testing and optimization research. It does not represent live
> Indian Railways operational data.

## Overview

Single fictional corridor used as the canonical operational world for the
frontend, backend APIs, E09 CP-SAT planner, E05 simulation, P17 decision
intelligence and P18 recovery:

- Corridor: **C-07 — Anandpur–Fatehgarh Main Line** (186.4 km, double line
  electrified, Demo Railway Zone / Central Division)
- Operational day: **2026-09-10** (timezone `Asia/Kolkata`)
- 6 stations (`STN-A` … `STN-F`: ANP / MGR / KDP / NRG / VPR / FGC)
- 8 sections (`SEC-01` … `SEC-08`: 5 main-line + freight bypass + loop siding
  + goods loop)
- 12 trains (2 premium P1, 6 express/superfast P2, 1 passenger P3,
  3 freight P4)
- 3 train movements (2 occupied, 1 completed)
- 5 maintenance tasks (4 block-requiring, 1 non-block)
- 5 assets (track / OHE / signalling / point machines)
- 2 disruption scenarios (`SCN-OVERRUN-01` maintenance overrun used for the
  P18 recovery demo, `SCN-TRACK-FAIL-01` speed restriction)

Note: the original task brief listed 11 train rows under a "12 trains"
heading; this dataset adds `TRN-12431 Fatehgarh Superfast` as the twelfth
train so the counts, API responses and documentation agree.

## Files

| File | Content |
| --- | --- |
| `corridor.json` | Corridor C-07 metadata |
| `stations.json` | 6 stations with km, platforms, loops, junction flags |
| `sections.json` | 8 sections with length, tracks, electrification, speed, headway |
| `trains.json` | 12 trains with type, priority, schedule, status, route |
| `train_movements.json` | 3 section occupancies with entry/exit and delay |
| `assets.json` | 5 assets with health score and criticality |
| `maintenance_tasks.json` | 5 tasks with windows, durations, block requirement |
| `disruptions.json` | 2 scenarios for P18 / simulation |

## Why synthetic

All station names, train numbers, timings and scenarios are invented for the
SIH demonstration. The architecture is designed so this seed can later be
replaced by authenticated railway operational feeds via an
`OperationalRepository` interface (`DemoSeedRepository` today;
`IndianRailwaysDataAdapter` / `ExternalFeedAdapter` in future) without
changing API contracts or engine interfaces.

## Backend mapping

The backend keeps its existing canonical domain contracts unchanged. The
demo seed loader (`backend/app/infrastructure/railway_demo/`) adapts the
flat demo JSON to those contracts:

- `PREMIUM_EXPRESS` / `SUPERFAST` → `EXPRESS` (existing `TrainType`)
- `ELECTRICAL` → `OHE`, `SIGNALLING` → `SIGNALING` (existing `Department`)
- `SIGNALLING` asset → `SIGNAL`, `POINT` stays `POINT`
- Flat demo trains → nested `Train{service, priority, ...}`
- Demo `priority` (1–4, 1 = highest) preserved on the domain object
- Extra demo-only fields (headway, section_type, delays, routes, windows)
  remain available in the raw JSON for E09 / E05 / P17 / P18

## Validation

Run from the repository root:

```bash
python scripts/validate_railway_demo.py
```

Checks: referential integrity (sections→stations, routes→sections,
movements→trains/sections, tasks/assets/disruptions→sections),
`entry < exit` for movements, `earliest_start < latest_finish` for tasks,
and expected counts (6 / 8 / 12 / 3 / 5 / 5 / 2).
