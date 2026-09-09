# P16 — COMPLETE

Branch: `antigravity/core`
Commit: (Pending Commit)

## Objective:
P16 implements the initial RailMind Risk Prediction Foundation. It predicts risks such as ASSET_FAILURE and SERVICE_DISRUPTION by evaluating asset conditions, defects, P10 maintenance priority, and P15 forecasts. The architecture cleanly separates feature building from the risk engine to ensure a scalable seam for future ML integration.

## Risk types:
- `ASSET_FAILURE`, `SERVICE_DISRUPTION`, `TRAIN_DELAY`, `MAINTENANCE_OVERRUN`, `ASSET_AVAILABILITY`, `OPERATIONAL_CONGESTION`.

## Risk model:
- `RiskPredictionEngine` interface with `DeterministicBaselineRiskEngine` implementation.
- Produces a heuristic `risk_score` (0-100) mapped to a `RiskLevel` (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- Does NOT fabricate a probability percentage unless statically justified (set to `None`).
- Returns explicitly weighted `RiskFactor`s representing exactly why the risk was predicted.

## P10 integration:
- Consumes `priority_context` safely in `StandardRiskFeatureBuilder`.
- Extracts heuristic priority scores as a contributing feature without duplicating P10 internals.

## P15 integration:
- Consumes `forecast_context` safely to generate `forecast_pressure_score` feature components.
- Evaluates forecast presence and appropriately limits risk quality if unavailable.

## Data quality:
- Introduces `RiskQuality` with levels (`HIGH`, `MEDIUM`, `LOW`, `INSUFFICIENT`).
- Gracefully degrades into an `INSUFFICIENT` / `LOW` risk result if zero valid evidence observations exist.

## Temporal leakage protection:
- The `RiskFeatureBuilder` explicitly validates all timestamps against the request's `requested_at` cutoff.
- Features like `defect.timestamp >= cutoff_time` are explicitly discarded, verified by `test_temporal_leakage_protection`.

## Scenario isolation:
- Predictions record `state_mode` (e.g., `MOCKED` vs `LIVE`) inside `Provenance`, ensuring synthetic risk can't be mistaken for real consequences.

## Explainability:
- Deterministic logic surfaces the exact driving factors and their mathematical contribution (e.g. `DEFECT_SEVERITY_SCORE contributes 40.0 to total risk`).
- Produces plain-language explanation tracing the primary driver.

## Provenance:
- Traces `data_state`, timestamp, generator version (`1.0.0`).

## Evaluation:
- Basic abstractions for Precision, Recall, F1 added (`evaluate_precision_recall`) to support future ML backtesting on categorical risk levels.

## Persistence:
- ORM mapping `RiskPredictionORM` provided.
- Alembic migration `709420d89d63` bound to the schema.

## Tests:
Backend: 79/79 PASS
Frontend typecheck: PASS
Frontend lint: PASS
Frontend tests: PASS
Frontend build: PASS

## Database validation:
Alembic migration logic successfully generated and validated by SQLAlchemy initialization within tests. Offline capability preserved.

## Known limitations:
- Fully relies on heuristic deterministic weighting.
- Impact vs Likelihood matrices are omitted until statistical probabilities can be confidently calibrated.

## Files changed:
- `backend/alembic/versions/709420d89d63_p16_risk_prediction_schema.py`
- `backend/app/api/v1/endpoints/risk.py`
- `backend/app/api/v1/router.py`
- `backend/app/application/services/risk_service.py`
- `backend/app/domain/engine/risk/baseline.py`
- `backend/app/domain/engine/risk/evaluation.py`
- `backend/app/domain/engine/risk/features.py`
- `backend/app/domain/engine/risk/interfaces.py`
- `backend/app/domain/models/risk.py`
- `backend/app/infrastructure/database/models.py`
- `backend/tests/test_risk.py`
- `docs/P16_Report.md`