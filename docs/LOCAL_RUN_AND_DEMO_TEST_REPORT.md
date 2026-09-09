# LOCAL RUN AND DEMO TEST REPORT

## Environment

| Component | Detail |
| :--- | :--- |
| OS | Windows |
| Python | 3.12 |
| Node | Next.js (v16.1.1) |
| Database mode | MOCKED (No postgres running natively) |
| Backend port | 8000 |
| Frontend port | 3000 |

## Startup

| Component | Status |
| :--- | :--- |
| Backend | PASS |
| Frontend | PASS |
| Health | PASS |

## Backend Endpoints

| Endpoint | Status | Result |
| :--- | :--- | :--- |
| `GET /health` | 200 | PASS |
| `GET /api/v1/trains` | 200 | PASS |
| `GET /api/v1/maintenance/tasks` | 200 | PASS |
| `POST /api/v1/maintenance/prioritize` | 200 | PASS |
| `POST /api/v1/planning/generate` | 202 | PASS |
| `POST /api/v1/simulations` | 202 | PASS |
| `POST /api/v1/intelligence/evaluate` | 200 | PASS |
| `POST /api/v1/recovery/assess` | 200 | PASS |

## Engine Compatibility

| Engine | Status | Notes |
| :--- | :--- | :--- |
| E02 (Priority) | PASS | Handled via Freebuff math module |
| E08 (Runtime) | PASS | Integrated correctly in endpoints |
| E09 (CP-SAT Planner) | PASS | Successfully generates async plan jobs |
| E05 (Simulation) | PASS | Resolves candidate generation successfully |

## Advanced Pipeline

| Pipeline | Status | Notes |
| :--- | :--- | :--- |
| P17 (Intelligence) | PASS | Returns expected Candidate assessments or `Insufficient Evidence` fallback seamlessly. |
| P18 (Recovery) | PASS | Handles valid `TRACK_FAILURE` and computes recovery proposals gracefully. |

## Frontend Integration

| Route | Loads | API Connected | Main Action |
| :--- | :--- | :--- | :--- |
| `/` | Yes | Yes | Dashboard Loads |
| `/operations` | Yes | Yes | Train schedules view |
| `/maintenance` | Yes | Yes | Tasks listing |
| `/planning` | Yes | Yes | Block scheduling UI |
| `/simulation` | Yes | Yes | Plan performance testing |
| `/decisions` | Yes | Yes | Intelligence summary |

## Full workflow
Operations → Maintenance → E02 → E09 → E05 → P17 → P18 : **PASS**

**FINAL RESULT: PASS**

## Exact Startup Commands

```bash
# 1. Start backend
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 2. Start frontend
cd frontend
npm run dev
```

## Demo URLs

- **Frontend:** http://localhost:3000
- **Backend:** http://127.0.0.1:8000
- **API Docs:** http://127.0.0.1:8000/docs