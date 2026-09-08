# P03: Shared Domain Contracts Report

## Overview
Phase P03 implemented the canonical shared domain contracts for the RailMind project. The contracts establish strongly-typed definitions for core railway concepts (Operations, Planning, Simulation, Disruption, Decision, Maintenance), forming the foundation for future backend components and ensuring consistency across the stack.

## Implementation Steps

1. **Contracts Folder Structure**: 
   - We created the canonical contracts within `frontend/contracts/` to ensure they are inside the TypeScript compilation boundary of the frontend app until the Python backend is fully structured.
   - We also created a proxy `contracts/` directory at the project root with a README explaining this design choice.

2. **Core Primitives & Branded IDs**:
   - `common/ids.ts`: Created branded types (`TrainId`, `BlockId`, `ISOTimestamp`) to prevent accidental identifier cross-assignment and guarantee type-level correctness.
   - `common/time.ts`: Added structures like `TimeInterval` and `DurationMinutes`.
   - `common/errors.ts`: Established structured `DomainError` shapes and stable error codes.

3. **Domain Segregation**:
   - Organized files logically into `infrastructure`, `maintenance`, `operations`, `planning`, `simulation`, `disruption`, `decision`, `events`, and `ai`.
   - Contracts map directly to domain concepts (e.g., `TrainImpact`, `Defect`, `RecoveryPlan`, `SimulationScenario`).

4. **Frontend Integration**:
   - Updated existing models in `frontend/domain/types/` to import base primitives (`ISOTimestamp`, enums) directly from the new contracts.
   - Preserved `BlockStatus` and `PlanStatus` overrides locally inside `domain/types` to avoid breaking frontend assumptions.
   - Updated mock services and fixture definitions (`demoCorridor.ts`) to be compatible with stricter types.
   - Registered wrapper types for new concepts in `frontend/domain/types/` and exported them out of `frontend/domain/index.ts`.

5. **Validation Layer**:
   - Added runtime validation tools (`validateTimeInterval`, `validateDuration`, etc.) inside `contracts/validation/`.
   - Verified that all these validations successfully handle logic like ensuring end timestamps follow start timestamps or checking duration limits.

6. **Testing**:
   - Added `frontend/tests/contracts-validation.test.ts` to exercise runtime assertions and prove cross-domain relationship shapes (MaintenanceTask → Block → TrainImpact → Plan) fit perfectly together.

## Validation Results
- `npm run typecheck`: Passed
- `npm run lint`: Passed
- `npm run test`: Passed (8 suites, 22 tests)
- `npm run build`: Passed

All checks green! The system is now ready for P04 (Algorithm Stubs).
