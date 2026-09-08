# P10 — Maintenance Priority Engine Report

## 1. Objective

P10 establishes a **deterministic, explainable Maintenance Priority Engine** that evaluates maintenance tasks and produces a ranked priority result. This creates the prerequisite intelligence layer between the constraint evaluator (P09) and the future block optimizer (P11).

## 2. Scope

- Deterministic, factor-weighted scoring (no ML, no random values)
- 7 independent priority factors
- Structured violations with evidence
- Missing-data handling (e.g., no linked defect)
- Priority class thresholds (CRITICAL / HIGH / MEDIUM / LOW)
- REST API endpoints for single-task and batch evaluation
- Clean extension point for future ML engine

## 3. Architecture

```text
POST /api/v1/engine/priority/evaluate
        ↓
PriorityService (Application Layer)
        ↓
DeterministicPriorityEngine (Domain Layer)
        ↓
Factor evaluators (criticality, severity, safety, urgency, impact, type, duration)
        ↓
PriorityResult (Structured Output)
```

## 4. Priority Factors and Weights

| Factor ID         | Weight | Source                          |
|---|---|---|
| criticality       | 0.25   | task.criticality / defect.criticality |
| defect_severity   | 0.20   | defect.severity                 |
| safety_critical   | 0.20   | defect.is_safety_critical       |
| urgency           | 0.15   | defect.urgency_hours            |
| train_impact      | 0.10   | num_train_impacts (caller-supplied) |
| task_type         | 0.05   | task.type                       |
| duration          | 0.05   | task.duration.expected          |

**Weights sum to 1.0.**

The final score = sum(contribution_i) × 100, giving a 0–100 range.

## 5. Priority Classes

| Class    | Score Range |
|---|---|
| CRITICAL | >= 75       |
| HIGH     | 55 – 74.9   |
| MEDIUM   | 30 – 54.9   |
| LOW      | < 30        |

## 6. Missing-Data Behavior

| Missing Data   | Behavior                              |
|---|---|
| No defect      | severity=0, safety=0, urgency=0       |
| Zero urgency_h | urgency normalized to 1.0 (max)       |
| 0 train impacts| train_impact contribution = 0         |

The engine never crashes on missing optional factors.

## 7. Explainability

Every `PriorityFactorResult` contains:
- `factor_id`, `factor_name`
- `raw_value` — human-readable input
- `normalized_value` — 0.0 to 1.0
- `weight` — configured contribution cap
- `contribution` — actual contribution to score
- `explanation` — human-readable reason
- `evidence` — machine-readable dict for frontend rendering

## 8. API Endpoints Added

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/engine/priority/evaluate` | Evaluate a single task by ID |
| POST | `/api/v1/engine/priority/evaluate-batch` | Evaluate multiple tasks, sorted highest first |

## 9. Files Changed

| File | Change |
|---|---|
| `backend/app/domain/engine/priority_models.py` | NEW — PriorityClass, PriorityFactorResult, PriorityResult |
| `backend/app/domain/engine/priority_engine.py` | NEW — DeterministicPriorityEngine + all factor evaluators |
| `backend/app/application/services/priority_service.py` | NEW — PriorityService (application orchestration) |
| `backend/app/api/v1/endpoints/priority.py` | NEW — FastAPI endpoints |
| `backend/app/api/v1/router.py` | MODIFIED — added priority router |
| `backend/app/application/services/maintenance_service.py` | MODIFIED — added get_defect_for_task() |
| `backend/tests/test_priority.py` | NEW — 25 tests |
| `docs/P10_Report.md` | NEW — this report |

## 10. Tests

25 tests across:
- Factor correctness (criticality, severity, safety, urgency, train impact, task type, duration)
- Priority class boundary thresholds
- Determinism (same input → same output)
- Missing-data handling (no defect)
- Explainability (all factors present, explanation string populated)
- Provenance (engine version and data_state)
- API integration (single and batch endpoints)

## 11. Real/Mocked/Stubbed Status

| Component | Status |
|---|---|
| Maintenance tasks | MOCKED (InMemoryMaintenanceRepository) |
| Defect data | MOCKED |
| Train impact count | Caller-supplied (STUBBED) |
| Priority calculation | DETERMINISTIC (not ML-calibrated) |

## 12. Freebuff Integration Boundary

`DeterministicPriorityEngine` is the concrete implementation of the implicit `PriorityEngine` interface. Freebuff can implement an ML-based engine using the same `evaluate(task, defect, num_train_impacts) -> PriorityResult` signature and swap it in through `PriorityService` without requiring API changes.

## 13. Future P11 Extension Points

P11 (Block Optimization Engine) should consume `PriorityResult.score` and `priority_class` as inputs to its objective function for prioritizing which maintenance tasks to include and in which windows. P10 does NOT optimize; it informs the optimizer.

## 14. Deferred Work

- Database persistence (P13)
- Real BDMS/TMS data sources
- ML-calibrated priority scores (Freebuff - future)
- Risk prediction integration
- Cascading delay factor
- Historical failure rate factor (requires real data)