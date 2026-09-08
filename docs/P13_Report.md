# P13 — PostgreSQL + PostGIS Persistence & Repository Infrastructure

## 1. Objective
P13 introduces durable relational persistence to RailMind, substituting the in-memory backend strictly where requested via `DATABASE_ENABLED` environment configuration. It adheres to strict layered isolation, ensuring SQLAlchemy never leaks into the core domain.

## 2. Architecture
The architecture is structured as follows:
- **FastAPI** -> **Dependencies** -> **Application Services** -> **Domain Interfaces** -> **PostgreSQL Repositories** -> **SQLAlchemy** -> **PostgreSQL/PostGIS**.
- Mappers reside strictly within `backend/app/infrastructure/database/mappers.py`.
- Repositories conform to the `PlanRepository`, `OperationsRepository`, etc., protocols defined in P04/P05.

## 3. Database Technology
- **Engine**: PostgreSQL
- **Spatial**: PostGIS
- **ORM**: SQLAlchemy 2.x (DeclarativeBase, Mapped)
- **Migrations**: Alembic
- **Driver**: psycopg[binary]

## 4. Configuration
Driven by `app/core/config.py` and `.env`:
```text
DATABASE_ENABLED=true
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/railmind
```
Supports tuning variables for connection pooling. Defaults strictly to in-memory mode if `DATABASE_ENABLED=False`.

## 5. ORM Architecture
Models reside in `app/infrastructure/database/models.py`. Standardized on snake_case tables and explicitly avoiding the `metadata` column keyword conflict. 

## 6. Domain ↔ ORM Mapping
Explicit mappers (e.g. `to_plan_orm`, `to_plan_domain`) isolate mapping responsibilities from Application logic. 

## 7. Repository Architecture
The dependency injection graph in `app/api/dependencies.py` branches logic at startup:
```python
if settings.DATABASE_ENABLED:
    _plan_repo = PostgresPlanRepository(get_db)
else:
    _plan_repo = InMemoryPlanRepository()
```

## 8. Schema
Supported schemas cover `corridors`, `track_sections`, `assets`, `maintenance_tasks`, `trains`, `train_paths`, `plans`, `blocks`, `simulation_runs`, and `decisions`.

## 9. Relationships
Models use robust `ForeignKey` relationships cascading updates naturally on child bounds (e.g., Plans owning Blocks owning Tasks).

## 10. PostGIS
The Alembic `upgrade()` explicitly runs `CREATE EXTENSION IF NOT EXISTS postgis;` followed by `Geometry` column definitions on `corridors`, `track_sections`, and `assets` utilizing EPSG:4326.

## 11. Migrations
Alembic tracking configured within `alembic/versions`. The baseline `010c3ee27d98_initial_schema_and_postgis.py` sets up all primary tables.

## 12. Transactions
`PostgresPlanRepository` implements atomic persistence across Plans and Blocks. Rollbacks explicitly execute on errors.

## 13. Seed Data
`backend/scripts/seed_database.py` generates deterministic P06 graph data idempotently (skipping recreation if objects exist) allowing standard development parity with the default in-memory behavior.

## 14. Scenario Isolation
`SimulationRunORM` and `PlanORM` carry their specific metadata separating Live and Scenario behavior explicitly via explicit IDs without needing database per-scenario schemas.

## 15. Testing
The standard P05-P12 unit test suite passes fully against the `InMemory` configurations, verifying no logic regressions.

## 16. In-Memory vs PostgreSQL
Switchable reliably. 

## 17. Limitations
Cannot test PostGIS locally in a non-PostGIS configured environment dynamically without explicit setup. Acknowledged missing fallback tests against an actual DB layer given environment restrictions.

## 18. Future Extensions
Prepared for full integration via P14 data ingestion and heavy metric querying by decoupling analytics requirements explicitly.