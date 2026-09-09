# P18 — COMPLETE

Branch: `antigravity/core`
Commit: (Pending Commit)

## Objective:
P18 establishes the Disruption & Recovery Engine Foundation. It introduces the ability to log structural disruption events (track failures, train delays) and systematically deduce topological and operational impacts. Crucially, P18 generates `RecoveryOptions` (such as `SHIFT_BLOCK` or `DEFER_MAINTENANCE`) intended to be structurally validated by P09, simulated by P12, optimized by P11, and ultimately decided upon by P17 and humans (P08), establishing a non-autonomous, immutable recovery pipeline.

## Pre-coding findings:
- No existing canonical concepts for `Disruption` or `RecoveryAssessment` existed in P13/P14 infrastructure.
- Plans natively possess `PlanVersion`, naturally affording base plan immutability during replanning.
- The pipeline inherently protects against autonomous execution by returning structural `RecoveryOptions` that act strictly as "candidate proposals". 

## Implemented:
- **Disruption Model**: Captures structured types (`TRACK_FAILURE`, `CONGESTION`), severity, and provenance tracking the exact event context without overwriting LIVE models.
- **Impact Assessment**: `DeterministicImpactAssessmentEngine` that extrapolates secondary impacts (affected trains, blocked paths, suspended tasks) through hierarchical spatial checks against context models.
- **Recovery Candidates**: `DeterministicRecoveryCandidateGenerator` generating structured alternative actions like `NO_ACTION`, `SHIFT_BLOCK`, or `DEFER_MAINTENANCE` depending on priority structures and block configurations.

## Constraint integration:
- Recovery candidates flag `constraint_status="UNKNOWN"` indicating they formally await P09 validation. Feasibility gates are recognized inherently as down-stream requirements.

## Risk/Forecast integration:
- Designed to consume P10 `priority_class` to ascertain if a canceled task induces downstream risk. Forecasts explicitly gate temporal bounds to prevent leakage.

## Decision Intelligence integration:
- Recovery Options embed empty `decision_intelligence_reference` properties to explicitly support feeding the generated plans into the `P17 Decision Intelligence` assessments.

## Governance:
- Maintains strict hands-off bounds. P18 never manipulates the approved plan or live train locations natively.

## Temporal safety:
- Explicit temporal check: Disruption `start_time` must precede `request_cutoff_time`. Future disruptions instantly trigger a rejection `ValueError`, proven through `test_recovery_temporal_leakage`.

## Scenario isolation:
- Mismatched `DataState` checks are built directly into `RecoveryService`. Generating recovery candidates from `LIVE` disruptions using `MOCKED` context environments throws validation blockers immediately.

## Plan immutability/version safety:
- Generating a recovery option assigns it a `recovery_option_id` alongside a reference to `base_plan_id`. The old plan remains intact, fulfilling auditing requirements.

## Persistence:
- ORM mapping `DisruptionORM` and `RecoveryAssessmentORM` created securely, persisting options via `JSONB`. Migrated under `8028420e157a`.

## Tests:
Backend: 84/84 PASS
Frontend typecheck: PASS
Frontend lint: PASS
Frontend tests: PASS
Frontend build: PASS

## Database validation:
Alembic migration `8028420e157a` correctly maps ORM schemas offline.

## Known limitations:
- Fully relies on deterministic baseline engines that naively increment block shifts rather than performing advanced geometric searches. This is by design, deferring deeper heuristics to the P11 optimizer.
- `NO_ACTION` is always considered unconditionally to establish baseline metrics.

## Files changed:
- `backend/alembic/versions/8028420e157a_p18_recovery_schema.py`
- `backend/app/api/v1/endpoints/recovery.py`
- `backend/app/api/v1/router.py`
- `backend/app/application/services/recovery_service.py`
- `backend/app/domain/engine/recovery/baseline.py`
- `backend/app/domain/engine/recovery/interfaces.py`
- `backend/app/domain/models/recovery.py`
- `backend/app/infrastructure/database/models.py`
- `backend/tests/test_recovery.py`
- `docs/P18_Report.md`