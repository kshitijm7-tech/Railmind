# P17 — COMPLETE

Branch: `antigravity/core`
Commit: (Pending Commit)

## Objective:
P17 establishes the AI Decision Intelligence Foundation. It synthesizes outputs from Simulation (P12) and Risk (P16) to provide a deterministic, human-readable recommendation for evaluating candidate plans. This is an explicit decision-support layer, producing evidence and trade-offs to aid the P08 Approval/Governance layer, without autonomous mutations.

## Decision Intelligence:
- **DecisionIntelligenceRequest**: Evaluates candidate plans using decision contexts, strict time horizons, and isolated state constraints.
- **DeterministicDecisionAssessmentEngine**: Calculates the relative viability of plans based on aggregated positive (completed maintenance) and negative (delay, residual risk) evidence signals.

## Evidence:
- **StandardDecisionEvidenceProvider**: Aggregates signals from simulation metrics and risk scoring models into `DecisionEvidence` units.
- Captures severity, direction, provenance, and plain-language impact statements.

## Recommendation:
- Dynamically assigns an overall score per candidate.
- Identifies the `recommended_plan_id` driven strictly by the highest evidence-backed score, preserving stable determinism in ties.

## Alternatives:
- Candidate assessments are ranked comprehensively, storing evidence IDs, strengths, weaknesses, and tradeoff descriptors.

## Trade-offs:
- Auto-generates tradeoff records outlining the exact delta (e.g., Score Advantage/Disadvantage) between the top recommended plan and runner-up alternatives.

## P10/P11/P12/P15/P16 integration:
- Designed to consume simulation delay / maintenance completed signals (P12) and risk factors (P16).
- Sits effectively after Optimization (P11) which filters the candidates evaluated here.

## Temporal safety:
- Explicit temporal check implemented: `ev.timestamp >= cutoff_time` strictly isolates evidence that was generated *after* the request `requested_at` marker. (Tested via `test_intelligence_temporal_leakage_and_scenario_isolation`).

## Scenario isolation:
- Mismatched `DataState` (e.g., LIVE vs MOCKED) is intercepted at the evidence extraction layer. Synthetic signals will never accidentally justify a LIVE recommendation.

## Provenance:
- Attaches provenance records to every generated `DecisionEvidence` and the outer `DecisionIntelligenceResult`, strictly referencing `DataSource.SYSTEM` and `1.0.0` generator versions.

## Persistence:
- ORM mapping `DecisionIntelligenceResultORM` provided, securely structured with JSONB backing for deeply nested evidence trees.
- Migrated under `35b5383a7ef0`.

## Tests:
Backend: 81/81 PASS
Frontend typecheck: PASS
Frontend lint: PASS
Frontend tests: PASS
Frontend build: PASS

## Database validation:
Alembic migration logic successfully generated and dynamically loaded into the test ORM mapping validation checks. Real PostGIS dependency deferred to P13 offline environment toggles.

## Known limitations:
- Fully deterministic heuristic model. Weighting scale currently hard-coded (`0.1` for delay minute, `0.5` for risk percentage, `5.0` per completed task).
- Statistical accuracy requires replacing `DeterministicDecisionAssessmentEngine` with a trained ML framework in the future.

## Files changed:
- `backend/alembic/versions/35b5383a7ef0_p17_decision_intelligence_schema.py`
- `backend/app/api/v1/endpoints/intelligence.py`
- `backend/app/api/v1/router.py`
- `backend/app/application/services/intelligence_service.py`
- `backend/app/domain/engine/intelligence/assessment.py`
- `backend/app/domain/engine/intelligence/evidence.py`
- `backend/app/domain/engine/intelligence/interfaces.py`
- `backend/app/domain/models/intelligence.py`
- `backend/app/infrastructure/database/models.py`
- `backend/tests/test_intelligence.py`
- `docs/P17_Report.md`