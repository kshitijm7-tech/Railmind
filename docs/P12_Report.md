# P12 — Railway Simulation & Digital Twin Engine

## 1. Objective
P12 provides the discrete-event simulation foundation for RailMind. It models deterministic train movement against track availability dictated by the generated maintenance blocks to accurately determine feasibility, constraints, and delays without mutating live production state.

## 2. Architecture
The architecture is structured under `SimulationService` which acts as the application layer orchestration invoking `DeterministicDiscreteEventSimulator` in the domain.
- State is deterministic and evaluated chronologically.
- `AsyncJob` ensures simulation can run asynchronously to conform with the P04 interface design.
- The Engine reads Plans, TrainPaths, Operational Windows, and Tasks to compute states and delays.

## 3. Simulation Model
Implemented via `DeterministicDiscreteEventSimulator`. An internal priority queue holds `SimEvent` components which get processed to evaluate logical sequence.

## 4. Domain Components
Added Pydantic models under `app.domain.models.simulation`:
- `SimulationRun`
- `SimulationResult`
- `SimulationEvent`
- `TrainSimulationState`
- `SectionSimulationState`

## 5. Event Model
Current events tracked:
- `SIMULATION_STARTED`
- `BLOCK_ACTIVATED` / `BLOCK_RELEASED`
- `TRAIN_ENTERED_SECTION` / `TRAIN_EXITED_SECTION`
- `TRAIN_BLOCKED`
- `MAINTENANCE_STARTED` / `MAINTENANCE_COMPLETED`
- `SIMULATION_COMPLETED`

## 6. Train Movement Model
Trains traverse paths strictly according to segment intervals. If a block covers the segment section, the train blocks.

## 7. Block/Maintenance Model
Blocks lock a specific section until their interval expires. Maintenance tasks bound to blocks will record completion successfully provided block time ≥ task duration.

## 8. Delay Calculation
When a train is blocked, it accrues `delay_minutes` representing wait time until the section clears. Future delays cascade.

## 9. Metrics
Returns standard KPIs:
- `total_delay_minutes`
- `blocked_trains`
- `completed_maintenance_tasks`
- `operational_impact_score`

## 10. Scenario Isolation
Simulator explicitly requires a `scenario_id` context and operates strictly on the derived in-memory snapshot—meaning it executes without ever applying side-effects to Live data.

## 11. API
New endpoints introduced under `/api/v1/simulations`:
- `POST /api/v1/simulations`
- `GET /api/v1/simulations/{run_id}`
- `GET /api/v1/simulations/{run_id}/events`
- `GET /api/v1/simulations/{run_id}/results`

## 12. Repository Design
`SimulationService` acts as a state store proxy (temporarily in-memory map) compatible with subsequent P13 PostgreSQL integrations.

## 13. Testing
Tests guarantee block conflict detection, delay accumulation, event trace structure, API validation, and full pipeline execution using mock environments.

## 14. Determinism Verification
The test `test_simulation_determinism_and_delay` verifies that two independent simulation instances seeded with identical inputs generate completely identical metric footprints and event streams.

## 15. Limitations
Currently ignores continuous velocity profiles, complex track configurations (like signaling distance logic), or automated platform reassignment logic—favoring robust discrete events for basic block vs path overlap logic.

## 16. Future Extensions
Designed to accommodate advanced physics (Rerouting, Headway constraints, and Energy models) by injecting an advanced `FutureAdvancedSimulator` algorithm below the application level without breaking API contracts.