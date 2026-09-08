# P08 - Decision & Governance Backend

## Objective
Implement the governance layer for RailMind, allowing human users to explicitly APPROVE, REJECT, or DEFER generated block plans and recommendations.

## Implemented Features

1. **Domain Models**:
   - `Decision`, `Approval`, `AuditEvent`, `ApproveDecisionBody`, `RejectDecisionBody`, and `DeferDecisionBody` mapped accurately from the TS contracts.
   - Enhanced `enums.py` with `DecisionStatus` and `UserRole`.

2. **Repositories**:
   - Created `InMemoryDecisionRepository` to store decisions.
   - Created `InMemoryAuditRepository` to store the audit log history of decision state transitions.

3. **Application Service**:
   - `DecisionService` implements the core logic: `get_all_decisions`, `get_decision`, `approve_decision`, `reject_decision`, and `defer_decision`.
   - Before taking an action, it validates that the `target_plan_id` corresponds to a valid existing plan, and that the current decision status is `PENDING`.
   - Records an immutable `AuditEvent` on every action (e.g., `PLAN_APPROVED`, `PLAN_REJECTED`, `PLAN_DEFERRED`), appending it to the `audit_history` string list of the decision object for tracability.

4. **API Endpoints**:
   - Registered endpoints at `/api/v1/decisions` and `/api/v1/decisions/{id}/*` under the `decision` router.
   - Exposed explicit POST methods for the state machine transitions (`approve`, `reject`, `defer`) that safely wrap API standard responses via `ApiResponse` and `ApiListResponse`.

5. **Testing**:
   - Wrote comprehensive API tests testing all endpoints and 404 behavior, all tests passed (`pytest`).
   - Ran `typecheck`, `lint`, `test`, and `build` successfully on the `frontend`.
