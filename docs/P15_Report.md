# P15 — COMPLETE

Branch: `antigravity/core`
Commit: (Pending Commit)

## Objective:
P15 implements the initial RailMind Forecasting Foundation. It provides an offline, deterministic predictive capability to forecast Train Traffic Demand, Maintenance Workload, and Operational Pressure, creating a clear architectural seam for future ML integration without modifying core operational logic or introducing heavyweight dependencies.

## Implemented:
- Forecasting Domain Models (`ForecastRequest`, `ForecastResult`, `ForecastQuality`, `ForecastObservation`)
- Forecasting Engine Interface (`FeatureExtractor`, `HistoricalDataProvider`, `ForecastEngine`)
- Application Service (`ForecastingService`) orchestrating requests and data boundaries.
- Evaluation metrics (`MAE`, `RMSE`, `MAPE`).
- FastAPI Endpoint `POST /api/v1/forecasting/generate`.

## Forecast models:
- **DeterministicRollingAverage**: A lightweight baseline forecaster that uses historical observations and groups/aggregates them into temporal buckets (time intervals) to project expected future load.

## Data-quality handling:
- Introduces `ForecastQuality` gate which explicitly tracks the availability of valid historical records.
- Categorizes forecast trust levels into `HIGH`, `MEDIUM`, `LOW`, and `INSUFFICIENT`.
- Generates transparent explanations tying valid history count to confidence.

## Temporal leakage protection:
- `TimeSeriesFeatureExtractor` actively filters any historical observations where `timestamp >= request.horizon.start`.
- Explictly tested via `test_feature_extractor_prevents_temporal_leakage` to prove future data cannot pollute baseline calculations.

## Scenario isolation:
- History fetches respect `DataState` (MOCKED vs LIVE).
- Forecasting parameters explicitly map requested states directly to the underlying `HistoricalDataProvider` without blending scenario data.

## Persistence:
- ORM mapping `ForecastResultORM` provided to support relational querying.
- Alembic migration `59b6f50ae003` introduced for schema binding (`forecast_results`).
- Transparent fallback for offline environments (PostgreSQL dependency decoupled via in-memory testing).

## Tests:
Backend: 75/75 PASS (Includes temporal leakage, metric verification, zero-data fallback, and baseline deterministic output).
Frontend typecheck: PASS
Frontend lint: PASS
Frontend tests: PASS
Frontend build: PASS

## Database validation:
- Alembic migration files manually configured for PostGIS/Postgres. Validated schema compilation. Database mapping successfully loaded during Pytest ORM mapping initialization.

## Known limitations:
- `HistoricalDataProvider` mock currently returns static deterministic fixtures; real implementation will require joining P14 `IngestionRecords` and `MaintenanceTask`/`Train` entities.
- Advanced ML models are stubbed out; deterministic baseline will drift without periodic seasonal adjustment updates.

## Files changed:
- `backend/alembic/versions/59b6f50ae003_p15_forecasting_schema.py`
- `backend/app/api/v1/endpoints/forecasting.py`
- `backend/app/api/v1/router.py`
- `backend/app/application/services/forecasting_service.py`
- `backend/app/domain/engine/forecasting/baseline.py`
- `backend/app/domain/engine/forecasting/evaluation.py`
- `backend/app/domain/engine/forecasting/features.py`
- `backend/app/domain/engine/forecasting/interfaces.py`
- `backend/app/domain/models/forecasting.py`
- `backend/app/infrastructure/database/models.py`
- `backend/app/infrastructure/forecasting/historical_provider.py`
- `backend/tests/test_forecasting.py`
- `docs/P15_Report.md`