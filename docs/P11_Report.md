# P11 — Block Optimization Engine

## 1. Objective
P11 implements the first deterministic **Block Optimization Engine** for RailMind. 
It balances priority value, operational utilization, and constraint violations (hard & soft) to generate a feasible maintenance plan.

## 2. Architecture
The architecture introduces `DeterministicBaselineOptimizer` under `OptimizationEngine`. 

```text
PlanningService (generates candidates)
      ↓
ConflictDetector (evaluates C1-C3 constraints)
      ↓
PriorityService (evaluates priority scores)
      ↓
DeterministicBaselineOptimizer (builds the optimal plan)
      ↓
OptimizationResult 
```

## 3. Optimization Formulation
**Maximize:**
- Priority Score (weight 1.0)
- Tasks Completed (weight 10.0)
- Window Utilization (weight 0.5)

**Minimize:**
- Train Impact / Soft Constraint Violations (weight 1.0)
- Operational Impact (weight 2.0)

## 4. Hard Constraints
- **C1/C2/C3:** Candidates failing hard constraints evaluated by P09 are strictly rejected.
- **C4:** `DeterministicBaselineOptimizer` strictly rejects overlapping blocks in the same section.

## 5. Soft Constraints
Soft violations incur a configurable train/operational impact penalty.

## 6. Objective Weights
The weights are defined in `OptimizationConfiguration`:
- `priority_weight = 1.0`
- `task_completion_weight = 10.0`
- `window_utilization_weight = 0.5`
- `soft_constraint_penalty = 1.0`

## 7. Solver Strategy
It uses a deterministic greedy strategy sorting tasks by priority and picking the combination that maximizes the objective delta without overlapping.

## 8. Deterministic Tie-breaking
Tasks are ordered primarily by `PriorityResult.score` and block overlapping dictates secondary exclusions.

## 9. P09 Integration
`ConflictDetector` output is leveraged to find candidates that have zero hard violations.

## 10. P10 Integration
`PriorityService` output generates the baseline weight for a specific task and factors into the objective.

## 11. API Changes
No API interface breaks. Integrated transparently into `POST /api/v1/planning/generate` using the AsyncJob boundary.

## 12. Plan Metrics
PlanMetrics now accurately aggregates the optimization breakdown into `ObjectiveTerm` lists.

## 13. Explainability
`OptimizationResult` exposes an `explanation` block detailing why tasks were selected or rejected.

## 14. Provenance
Engine version (`1.0.0`) and name (`DeterministicBaselineOptimizer`) tracked inside `PlanVersion` and `Provenance`.

## 15. Tests
`test_optimization.py` validates priority routing, overlapping exclusion, and hard constraint filtering.

## 16. Mocked/Stubbed/Real Status
Uses deterministic models but mocked repository data.

## 17. Freebuff Integration Boundary
`OptimizationEngine` exposes an interface taking in constraints and priority values. Freebuff can seamlessly override `DeterministicBaselineOptimizer` via injection in `PlanningService`.

## 18. P12 Extension Points
Provides the backbone for comparison of generated scenarios (`ComparePlansResponse`).

## 19. Deferred Work
Complex constraint propagation (CP-SAT/MILP) and real ML impact calculation deferred.