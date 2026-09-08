RAILMIND
Railway Maintenance, Operations & Block Intelligence Platform
Technical Requirements Document — v1.0
SIH Problem Statement: SIH26027
Domain: Indian Railways / Railway Operations / AI Decision Intelligence
Product: RAILMIND
Document Status: Engineering Baseline
Architecture Classification: Industry-grade, MVP-deployable, production-extensible
Primary Release: Tier 1 — SIH MVP
Future Releases: Tier 2 Pilot → Tier 3 Railway Intelligence Platform
________________________________________
1. Technical Vision
RAILMIND shall be implemented as a railway decision-intelligence platform, not as a single machine-learning application.
The fundamental technical responsibility split is:
ML predicts → Rules constrain → Optimization decides → Simulation evaluates → Decision Intelligence explains → Human approves → State Engine records → System adapts.
This separation is a core architectural requirement. The blueprint explicitly establishes that ML must not become the final authority, hard constraints must not be optimized away, simulation must not directly execute changes, and human authorization remains the final decision boundary.
RAILMIND therefore consists of:
1.	Railway Data Platform
2.	Integration Fabric
3.	Railway State Engine
4.	ML Intelligence Layer
5.	Rules & Policy Engine
6.	Optimization Engine
7.	Digital Twin / Simulation Engine
8.	Disruption & Recovery Engine
9.	Decision Intelligence Engine
10.	Explainability Engine
11.	Human Approval Layer
12.	Audit & Governance Layer
13.	Frontend Command Interface
________________________________________
2. Engineering Philosophy
2.1 Architecture Principle
RAILMIND will use:
Modular Monolith + Asynchronous Compute Workers
for Tier 1.
It will NOT use a microservice architecture for the SIH MVP.
The blueprint explicitly recommends a modular monolith with logical module boundaries inside a FastAPI service, while allowing optimization and simulation to execute through asynchronous workers.
This provides:
•	fast development
•	low infrastructure complexity
•	easier debugging
•	deterministic demos
•	clear domain boundaries
•	straightforward local deployment
•	future service extraction
The architecture must nevertheless follow service-oriented internal boundaries so that modules can later become independently deployable services.
________________________________________
3. Tiered Technical Architecture
Tier	Purpose	Deployment
Tier 1	SIH MVP	Modular monolith
Tier 2	Pilot	Modular services + event-driven integration
Tier 3	Enterprise platform	Distributed services + multi-zone infrastructure
Tier 1
Build:
•	PostgreSQL/PostGIS
•	FastAPI
•	React/Next.js
•	CP-SAT
•	ML models
•	simulation
•	Monte Carlo
•	state versioning
•	disruption recovery
•	RBAC
•	audit
•	Docker
Tier 2
Add:
•	real railway adapters
•	event streaming
•	deeper RBAC
•	model monitoring
•	production observability
•	multi-division architecture
•	scalable workers
Tier 3
Potentially add:
•	Kubernetes
•	Kafka/Redpanda
•	distributed optimization
•	GNN
•	graph database where justified
•	multi-zone deployment
•	advanced digital twin
•	continuous learning
•	enterprise identity
•	high-scale GIS
The original blueprint explicitly places Kubernetes, Kafka/Redpanda, OpenTelemetry, Prometheus/Grafana, GNNs and other large-scale infrastructure in the Tier 2/3 roadmap rather than requiring them for the SIH build.
________________________________________
4. High-Level System Architecture
                    ┌──────────────────────────────┐
                    │ EXISTING RAILWAY SYSTEMS     │
                    │ TMS / SMMS / TDMS / BDMS     │
                    │ COA / GIS / Timetable / AMS  │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │      INTEGRATION FABRIC       │
                    │                              │
                    │ API Adapters                  │
                    │ CSV/JSON Ingestion            │
                    │ Event Gateway                 │
                    │ Validation                    │
                    │ Provenance                    │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
        ┌───────────────────────────────────────────────────┐
        │             RAILWAY DATA PLATFORM                 │
        │                                                   │
        │ Canonical Model │ PostgreSQL │ PostGIS            │
        │ Historical Data │ Event Store│ Network Model      │
        └──────────────────────┬────────────────────────────┘
                               │
                               ▼
        ┌───────────────────────────────────────────────────┐
        │                RAILWAY STATE ENGINE                │
        │                                                   │
        │ PLAN │ ACTUAL │ PREDICTION │ SCENARIO             │
        │ State Versions │ Dependency Graph                 │
        └──────────────┬─────────────────┬──────────────────┘
                       │                 │
             ┌─────────▼───────┐ ┌──────▼──────────────┐
             │ INTELLIGENCE    │ │ RULES / POLICY      │
             │ ML              │ │ ENGINE              │
             │                 │ │                     │
             │ Duration        │ │ Hard Constraints    │
             │ Delay           │ │ Soft Constraints    │
             │ Priority        │ │ Policy Versions     │
             │ Failure Risk    │ │                     │
             └─────────┬───────┘ └──────┬──────────────┘
                       │                 │
                       └────────┬────────┘
                                ▼
                  ┌──────────────────────────┐
                  │ OPTIMIZATION ENGINE      │
                  │                          │
                  │ OR-Tools CP-SAT          │
                  │ Block Planning            │
                  │ Bundling                   │
                  │ Train Coordination         │
                  │ Recovery                   │
                  └─────────────┬────────────┘
                                │
                                ▼
                  ┌──────────────────────────┐
                  │ DIGITAL TWIN / SIMULATOR  │
                  │                          │
                  │ What-if                  │
                  │ Delay propagation        │
                  │ Monte Carlo               │
                  └─────────────┬────────────┘
                                │
                                ▼
                  ┌──────────────────────────┐
                  │ DECISION INTELLIGENCE     │
                  │                          │
                  │ Ranking                  │
                  │ Risk                     │
                  │ Alternatives              │
                  │ Explanation               │
                  └─────────────┬────────────┘
                                │
                                ▼
                  ┌──────────────────────────┐
                  │ HUMAN APPROVAL            │
                  │                          │
                  │ Approve / Modify / Reject│
                  └─────────────┬────────────┘
                                │
                                ▼
                  ┌──────────────────────────┐
                  │ CONTROLLED EXECUTION     │
                  └─────────────┬────────────┘
                                │
                                ▼
                  ┌──────────────────────────┐
                  │ ACTUAL OUTCOME            │
                  │ → STATE ENGINE            │
                  └──────────────────────────┘
This follows the blueprint’s canonical architecture from integration through state, intelligence, rules, optimization, simulation, decision intelligence and human approval.
________________________________________
5. Recommended Technology Stack
5.1 Frontend
Primary
•	React
•	Next.js
•	TypeScript
UI
•	Tailwind CSS
•	shadcn/ui
•	Recharts
•	TanStack Table
•	React Query / TanStack Query
•	Zod
•	React Hook Form
Network Visualization
Tier 1:
•	SVG / Canvas-based corridor visualization
Tier 2:
•	MapLibre
•	Deck.gl
The blueprint specifies React + Next.js + TypeScript for Tier 1 and MapLibre/Deck.gl as a future large-scale visualization capability.
________________________________________
6. Backend Architecture
6.1 Language
Python 3.12+
Reason:
•	ML ecosystem
•	OR-Tools
•	scientific computing
•	simulation
•	FastAPI
•	rapid development
•	strong data-processing ecosystem
6.2 API Framework
FastAPI
Supporting libraries:
•	Pydantic v2
•	SQLAlchemy 2
•	Alembic
•	Uvicorn
•	httpx
6.3 Backend Structure
backend/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── logging.py
│   │   └── exceptions.py
│   │
│   ├── domain/
│   │   ├── network/
│   │   ├── assets/
│   │   ├── maintenance/
│   │   ├── trains/
│   │   ├── resources/
│   │   ├── blocks/
│   │   ├── incidents/
│   │   ├── plans/
│   │   ├── scenarios/
│   │   └── recommendations/
│   │
│   ├── state/
│   │   ├── state_engine.py
│   │   ├── versioning.py
│   │   └── dependency_graph.py
│   │
│   ├── intelligence/
│   │   ├── duration/
│   │   ├── delay/
│   │   ├── priority/
│   │   └── risk/
│   │
│   ├── rules/
│   │   ├── hard_constraints.py
│   │   ├── soft_constraints.py
│   │   └── policies/
│   │
│   ├── optimization/
│   │   ├── cp_sat/
│   │   ├── objective.py
│   │   ├── constraints.py
│   │   └── recovery.py
│   │
│   ├── simulation/
│   │   ├── engine.py
│   │   ├── scenarios.py
│   │   └── monte_carlo.py
│   │
│   ├── decision/
│   │   ├── ranking.py
│   │   ├── alternatives.py
│   │   └── explanation.py
│   │
│   ├── integrations/
│   │   ├── csv/
│   │   ├── json/
│   │   └── adapters/
│   │
│   ├── audit/
│   │
│   └── workers/
│
├── tests/
├── migrations/
└── scripts/
________________________________________
7. Database Architecture
7.1 Primary Database
PostgreSQL
7.2 Spatial Extension
PostGIS
The blueprint specifies PostgreSQL + PostGIS as the Tier-1 data platform.
________________________________________
8. Logical Data Domains
The database shall be organized around these domains:
Network
•	stations
•	sections
•	tracks
•	junctions
•	routes
•	topology
Assets
•	asset
•	asset_type
•	asset_health
•	asset_criticality
Maintenance
•	maintenance_task
•	task_dependency
•	task_history
•	task_duration_observation
Trains
•	train
•	train_schedule
•	train_priority
•	train_route
•	train_delay_observation
Resources
•	crew
•	crew_skill
•	equipment
•	resource_availability
Blocks
•	block
•	block_window
•	block_task
•	block_train_impact
State
•	state_version
•	state_snapshot
•	state_change
•	scenario_branch
Intelligence
•	model_registry
•	prediction
•	prediction_feature_snapshot
•	model_evaluation
Optimization
•	optimization_run
•	optimization_solution
•	optimization_constraint_trace
•	objective_breakdown
Decisions
•	recommendation
•	recommendation_alternative
•	approval
•	decision
Events
•	railway_event
•	incident
•	event_impact
Audit
•	audit_log
________________________________________
9. Canonical Entity Model
Core entities:
RailwayNetwork
 ├── Station
 ├── Section
 │    ├── Asset
 │    └── Track
 └── Route

MaintenanceTask
 ├── Asset
 ├── Section
 ├── Department
 ├── Resource
 └── Dependency

Train
 ├── Route
 ├── Schedule
 └── Priority

Block
 ├── Section
 ├── MaintenanceTask[]
 ├── Resource[]
 └── TrainImpact[]

Incident
 ├── Section
 ├── Asset
 └── Impact[]

Recommendation
 ├── Plan
 ├── StateVersion
 ├── Predictions
 ├── Alternatives
 └── Explanation
The canonical model deliberately decouples RAILMIND from individual source-system schemas.
________________________________________
10. State Engine
The State Engine is one of the most important components.
RAILMIND must distinguish four state types:
PLAN
ACTUAL
PREDICTION
SCENARIO
PLAN
What the system intends to execute.
ACTUAL
What is actually happening.
Example:
BLOCK B102
planned_end = 02:00
actual_end = 02:45
PREDICTION
What ML/simulation believes will happen.
Example:
predicted_duration = 132 min
P90_duration = 161 min
overrun_probability = 0.18
SCENARIO
A hypothetical state branch.
Example:
Scenario A:
Block at 01:00

Scenario B:
Block at 03:00
Scenario B must never mutate the live operational state.
The blueprint explicitly requires copy-on-write scenario branches.
________________________________________
11. State Versioning
Every material state change generates a new version.
Example:
State v100
      ↓
BLOCK_OVERRUN
      ↓
State v101
      ↓
Recovery optimization
      ↓
State v102
Every recommendation must store:
state_version
constraint_version
objective_version
model_version
solver_version
This makes the system reproducible.
________________________________________
12. Machine Learning Architecture
RAILMIND should NOT have one giant model.
It should have four independent intelligence models for Tier 1.
Model 1 — Maintenance Priority Model
Purpose:
Determine maintenance urgency.
Inputs
•	asset criticality
•	overdue duration
•	failure risk
•	safety flag
•	downstream impact
•	task type
•	asset type
•	section criticality
Output
priority_score
priority_class
reason_codes
confidence
Example:
T102

Priority: CRITICAL
Score: 0.91

Reasons:
+ Asset criticality
+ 5 days overdue
+ High failure risk
+ Safety flag
The blueprint’s default priority weighting is configurable rather than hard-coded.
________________________________________
13. Model 2 — Maintenance Duration Prediction
Purpose:
Predict realistic task duration.
Inputs
task_type
department
asset_type
section_criticality
crew_size
historical_duration
time_of_day
similar_task_history
Outputs
P10 duration
Expected duration
P90 duration
Overrun probability
Confidence
Recommended model
XGBoost Regressor
Alternative baseline:
Random Forest Regressor
The blueprint specifically calls for tabular ML using scikit-learn/XGBoost for Tier 1.
________________________________________
14. Model 3 — Train Delay Prediction
Purpose:
Estimate direct and downstream train impact caused by blocks.
Inputs
train_type
train_priority
scheduled_time
section
block_duration
block_start
number_of_affected_trains
historical_delay
time_of_day
network_congestion
Outputs
direct_delay
downstream_delay
total_predicted_delay
confidence
Tier 1 approach
Start with:
XGBoost / Gradient Boosting
and a deterministic graph propagation layer using NetworkX.
Do NOT build a GNN initially.
The blueprint explicitly defers GNNs to a later phase.
________________________________________
15. Model 4 — Asset Failure/Risk Model
Purpose:
Estimate likelihood that an asset becomes problematic.
Inputs
asset_age
asset_type
maintenance_history
failure_history
criticality
days_since_last_service
task_backlog
condition_score
Output
failure_risk
risk_class
confidence
Recommended model
Tier 1:
XGBoost Classifier
Fallback:
Random Forest
________________________________________
16. Total ML Model Count
Tier 1
Model	Algorithm
Maintenance Priority	XGBoost / weighted interpretable score
Duration Prediction	XGBoost Regressor
Delay Prediction	XGBoost + NetworkX
Asset Failure Risk	XGBoost Classifier
Total
4 ML models
However, only the models that have sufficient training data should be enabled.
The deterministic priority score remains important because the system must continue functioning even if the ML model is unavailable.
________________________________________
17. ML Design Principle
Every model must implement a common interface:
class PredictionModel(Protocol):

    def predict(self, features):
        ...

    def predict_with_uncertainty(self, features):
        ...

    def get_version(self):
        ...

    def explain(self, features):
        ...
This means:
XGBoost
   ↓
can later be replaced by
LightGBM
   ↓
PyTorch
   ↓
GNN
without changing the rest of RAILMIND.
________________________________________
18. ML Model Registry
Tier 1 can use a database-backed lightweight registry.
Each model stores:
model_id
model_name
model_type
version
training_dataset_version
feature_schema_version
training_timestamp
metrics
artifact_location
status
Example:
duration-model
version: 1.0.0
algorithm: XGBoost
dataset: synthetic-v1
RMSE: 14.2
MAE: 9.7
status: ACTIVE
________________________________________
19. Model Evaluation
Every predictive model must be evaluated against a baseline.
Regression metrics
•	MAE
•	RMSE
•	R²
•	MAPE/SMAPE where appropriate
Classification
•	Precision
•	Recall
•	F1
•	ROC-AUC
•	PR-AUC
•	calibration
Operational metrics
More important than raw ML metrics:
•	schedule improvement
•	delay reduction
•	maintenance completion
•	overrun-risk reduction
RAILMIND is a decision system, so predictive accuracy alone is not the final success criterion.
________________________________________
20. Rules Engine
The Rules Engine is deterministic.
It must never depend on an LLM.
Rules are divided into:
Hard Constraints
Cannot be violated.
Examples:
•	section cannot host conflicting blocks
•	incompatible trains cannot occupy blocked section
•	task dependency cannot be violated
•	crew must be qualified
•	block must fit inside allowed window
•	task must fit duration bounds
•	resource cannot be double-booked
•	deadline constraints
Soft Constraints
Can be violated at a measurable cost.
Examples:
•	preferred maintenance window
•	preferred crew
•	preferred bundling
•	preferred train impact
•	preferred night window
________________________________________
21. Constraint Versioning
Every ruleset receives:
constraint_set_id
version
effective_from
effective_to
created_by
Example:
constraint-set
v1.2.0
An optimization run must reference the exact constraint version.
________________________________________
22. Optimization Engine
Primary Solver
Google OR-Tools CP-SAT
The blueprint defines CP-SAT as the Tier-1 scheduling engine.
CP-SAT will handle:
•	maintenance task assignment
•	block selection
•	block timing
•	task bundling
•	resource assignment
•	train-block coordination
•	recovery planning
________________________________________
23. Optimization Decision Variables
Core variables:
x[t,w] = task t assigned to window w

y[w] = block window activated

z[t,r] = task t assigned to resource r

delay[r] = predicted train delay

unscheduled[t] = task not scheduled
________________________________________
24. Hard Constraints
At minimum:
1. Task assignment
A task can be assigned to at most one block.
2. Block exclusivity
A conflicting section cannot have overlapping blocks.
3. Resource availability
A resource cannot serve two incompatible tasks simultaneously.
4. Crew qualification
Only qualified crew may execute the task.
5. Task duration
Block duration must accommodate assigned work.
6. Dependencies
Dependent tasks must respect precedence.
7. Deadline
Maintenance tasks must finish before their deadline where mandatory.
8. Train movement
Unsafe train/block conflicts are forbidden.
9. Possession boundaries
Blocks must remain within permitted windows.
________________________________________
25. Optimization Objective
The objective is:
Minimize:

α × Train Delay
+
β × Unscheduled Maintenance Priority
+
γ × Number of Blocks
+
δ × Block Overrun Risk
-
ε × Bundling Benefit
Default configurable weights:
α = 5
β = 4
γ = 1
δ = 2
ε = 1
These are configuration values, not hard-coded constants.
The frontend should expose these as controlled planning preferences rather than allowing arbitrary unsafe changes.
________________________________________
26. Robust Scheduling
RAILMIND must not optimize using only a single duration estimate.
For each maintenance task:
P10
Expected
P90
After CP-SAT generates a candidate:
Monte Carlo
N = 200 simulations
Each simulation samples task durations from the defined uncertainty band.
Outputs:
P(overrun)
P(plan violation)
Expected delay
Worst-case delay
Maintenance completion probability
The blueprint explicitly specifies 200 Monte Carlo draws for Tier 1.
________________________________________
27. Digital Twin
The Tier-1 digital twin is computational, not 3D.
It maintains:
Network state
Train state
Block state
Maintenance state
Resource state
Delay state
It must use the same canonical model as the optimizer.
This prevents:
Optimizer thinks:
Section S4 is available

Simulator thinks:
Section S4 is occupied
________________________________________
28. Simulation Engine
Recommended implementation:
Python
+
SimPy / custom discrete-event simulation
+
NetworkX
+
NumPy
Simulation modes:
Mode 1
Baseline plan.
Mode 2
Alternative plan.
Mode 3
Block overrun.
Mode 4
Track unavailable.
Mode 5
Train delay.
Mode 6
What-if scenario.
________________________________________
29. Scenario Architecture
Every scenario receives:
scenario_id
parent_state_version
scenario_name
changes[]
created_at
status
Example:
LIVE
  │
  ├── Scenario A
  │    Block at 01:00
  │
  ├── Scenario B
  │    Block at 03:00
  │
  └── Scenario C
       Block bundled with S&T work
No scenario is allowed to modify LIVE.
________________________________________
30. Disruption Engine
Supported Tier-1 events:
BLOCK_OVERRUN
TRACK_UNAVAILABLE
TRAIN_DELAY
RESOURCE_UNAVAILABLE
________________________________________
31. Block Overrun Recovery
Flow:
BLOCK_OVERRUN
      ↓
Update ACTUAL state
      ↓
Create new state version
      ↓
Find affected trains
      ↓
Predict delay propagation
      ↓
Identify affected/downstream windows
      ↓
Re-run CP-SAT
      ↓
Generate candidates
      ↓
Run simulation
      ↓
Run Monte Carlo
      ↓
Rank candidates
      ↓
Human approval
      ↓
Recovery plan
The blueprint specifically requires affected/downstream windows to be re-solved rather than unnecessarily solving the entire horizon.
________________________________________
32. Track Unavailable Recovery
Flow:
TRACK_UNAVAILABLE
       ↓
Incident Classification
       ↓
Dependency Graph
       ↓
Find impacted sections
       ↓
Invalidate dependent plans
       ↓
Identify affected trains/tasks/blocks
       ↓
Generate recovery candidates
       ↓
CP-SAT re-solve
       ↓
Simulation
       ↓
Ranking
       ↓
Human approval
Recovery uses the same optimization model with updated state rather than creating a completely separate recovery algorithm.
________________________________________
33. Decision Intelligence Layer
The Decision Engine converts:
predictions
+
constraints
+
optimization
+
simulation
+
risk
into ranked options.
Example:
Recommendation R102

Option A
Expected delay: 11 min
Overrun risk: 9%
Maintenance completion: 100%

Option B
Expected delay: 37 min
Overrun risk: 24%
Maintenance completion: 100%

Recommended:
Option A
________________________________________
34. Explainability Engine
Every recommendation must contain:
recommendation_id
state_version
plan_version
model_version

recommended_action

expected_outcome

affected_trains
affected_tasks
affected_resources

constraint_trace

objective_breakdown

alternatives[]

prediction_evidence
This is explainability by construction, rather than generating an explanation after the fact.
The blueprint explicitly requires recommendations to be traceable to structured inputs.
________________________________________
35. Optional LLM Layer
An LLM is not required for the core RAILMIND decision loop.
If included:
Structured system output
        ↓
LLM
        ↓
Natural-language explanation
Never:
LLM
 ↓
optimization decision
The LLM may explain:
“Block B was selected because it completes two critical maintenance tasks while producing lower predicted train delay and lower overrun risk.”
But the LLM must not invent:
•	delay values
•	train numbers
•	risk percentages
•	constraints
•	asset status
All numbers must originate from structured system output.
________________________________________
36. Graph Architecture
Tier 1:
NetworkX
Graph nodes:
Station
Section
Asset
Block
Train
Edges:
connected_to
depends_on
affects
routes_through
conflicts_with
The graph is used for:
•	dependency traversal
•	impact analysis
•	delay propagation
•	disruption analysis
A dedicated graph database is not required for Tier 1.
________________________________________
37. API Architecture
Base URL:
/api/v1
Network
GET /network
GET /network/stations
GET /network/sections
GET /network/topology
Assets
GET /assets
GET /assets/{id}
Maintenance
GET /maintenance
POST /maintenance
GET /maintenance/{id}
POST /maintenance/prioritize
Trains
GET /trains
GET /trains/{id}
Blocks
GET /blocks
POST /blocks/generate
GET /blocks/{id}
Plans
POST /plans/generate
GET /plans/{id}
POST /plans/{id}/simulate
POST /plans/{id}/approve
POST /plans/{id}/reject
Scenarios
POST /scenarios
GET /scenarios/{id}
POST /scenarios/{id}/simulate
Disruptions
POST /disruptions
GET /disruptions/{id}
POST /disruptions/{id}/recover
Recommendations
GET /recommendations
GET /recommendations/{id}
Events
POST /events
GET /events
Decisions
POST /decisions
GET /decisions
These endpoint families correspond to the Tier-1 API surface defined in the blueprint.
________________________________________
38. Asynchronous Job Architecture
Optimization and simulation should not block HTTP requests.
Example:
POST /plans/generate
       ↓
job_id
       ↓
Worker
       ↓
CP-SAT
       ↓
Simulation
       ↓
Monte Carlo
       ↓
Result
Tier 1
Use:
•	FastAPI
•	Background worker
•	Redis optional
Tier 2
Move to:
•	Redis
•	Celery/RQ or equivalent
•	event-driven workers
Tier 3
Potential:
•	Kafka/Redpanda
•	dedicated optimization workers
•	distributed job orchestration
________________________________________
39. Messaging
Tier 1:
In-process events
+
optional Redis
Events:
TASK_CREATED
TASK_UPDATED
BLOCK_CREATED
BLOCK_APPROVED
BLOCK_OVERRUN
TRAIN_DELAYED
TRACK_UNAVAILABLE
PLAN_INVALIDATED
RECOVERY_REQUIRED
PLAN_APPROVED
Production evolution:
Kafka / Redpanda
The blueprint explicitly places Kafka/Redpanda at production event volume rather than making it an MVP dependency.
________________________________________
40. Integration Architecture
Every external railway system must connect through an adapter.
                 RAILMIND
                    │
              Integration Port
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
       TMS         SMMS        GIS
       Adapter     Adapter     Adapter
Interfaces:
class RailwaySystemAdapter(Protocol):

    def fetch(self, request): ...
    def validate(self, payload): ...
    def normalize(self, payload): ...
    def get_provenance(self): ...
Tier 1 adapters:
CSVAdapter
JSONAdapter
SyntheticRailwayAdapter
Tier 2:
TMSAdapter
SMMSAdapter
TDMSAdapter
BDMSAdapter
GISAdapter
________________________________________
41. Data Validation
Every incoming dataset passes:
Schema validation
      ↓
Type validation
      ↓
Range validation
      ↓
Referential validation
      ↓
Temporal validation
      ↓
Railway-domain validation
      ↓
Canonical normalization
Invalid records must not silently enter the optimization engine.
________________________________________
42. Data Provenance
Each imported record should retain:
source_system
source_record_id
ingestion_timestamp
schema_version
data_version
checksum
This becomes essential when Tier 2 integrates real railway systems.
________________________________________
43. Security Architecture
Tier 1 Roles
Minimum:
PLANNER
CONTROLLER
APPROVER
The blueprint specifies these three minimum roles for the MVP.
Permissions:
Action	Planner	Controller	Approver
View	✓	✓	✓
Generate Plan	✓	✓	✓
Simulate	✓	✓	✓
Modify	✓	✓	✓
Approve	✗	✗	✓
Reject	✗	✗	✓
Execute	✗	Controlled	Authorized
________________________________________
44. Authentication
Tier 1:
•	JWT
•	password hashing
•	refresh tokens
•	role-based authorization
Tier 2:
•	SSO
•	enterprise identity
•	division/zone scoped permissions
Tier 3:
•	enterprise IAM
•	MFA
•	privileged access management
________________________________________
45. Audit Architecture
Every material action creates an append-only record.
audit_id
user_id
role
action
timestamp
state_version
previous_value
new_value
ip/session metadata
Optimization records additionally store:
constraint_version
objective_weights
model_versions
solver_version
The blueprint explicitly requires this reproducibility model.
________________________________________
46. API Security
Requirements:
•	request validation
•	authentication
•	authorization
•	rate limiting
•	input sanitization
•	structured error responses
•	CORS restrictions
•	secure headers
•	secrets through environment/secret manager
•	no credentials in source code
________________________________________
47. Observability
Tier 1
Implement:
Structured logging
JSON logs:
{
  "timestamp": "...",
  "service": "optimizer",
  "run_id": "OPT-102",
  "state_version": "v1021",
  "duration_ms": 1834,
  "status": "success"
}
Metrics
Track:
API latency
CP-SAT solve time
simulation time
Monte Carlo time
optimization failures
prediction latency
database latency
job queue depth
Tier 2+
Add:
•	OpenTelemetry
•	Prometheus
•	Grafana
•	distributed tracing
The blueprint identifies these as Tier 2/3 observability components.
________________________________________
48. Performance Requirements
Tier 1 targets:
Full optimization
< 10 seconds
Disruption re-plan
< 2 seconds target
for the bounded MVP dataset.
UI
< 1 second
for normal corridor browsing and recommendation viewing.
These targets are directly defined in the blueprint.
________________________________________
49. Determinism
Every simulation and optimization run must support:
random_seed
dataset_version
model_version
solver_version
constraint_version
objective_weights
Therefore:
same input
+
same configuration
+
same seed
=
same result
This is particularly important for the SIH demonstration.
________________________________________
50. Fault Tolerance
The system must gracefully handle:
ML unavailable
Fallback:
deterministic rules / statistical baseline
Optimizer unavailable
Display:
optimization unavailable
last valid plan
No unsafe automatic execution.
Database unavailable
Application enters:
read-only/degraded mode
Simulation failure
Recommendation must not be marked validated.
Invalid incoming data
Reject and quarantine the event.
________________________________________
51. Offline Mode
Tier 1 must operate without live railway integrations.
Synthetic Dataset
      ↓
Canonical Data
      ↓
State Engine
      ↓
ML
      ↓
Optimizer
      ↓
Simulation
      ↓
UI
Offline/simulation mode is a first-class Tier-1 operating mode, not an emergency fallback.
________________________________________
52. Demo Dataset
Recommended baseline:
1 division
1 bounded corridor
6 stations
9 track sections
72-hour horizon

48 trains
34 passenger
14 goods

22 maintenance tasks
3 overdue
4 critical

4 departments

4–6 candidate windows per section/day

2 shifts
3–6 crews/shift

1 block overrun
+45 minutes

1 TRACK_UNAVAILABLE event
This sizing is deliberately designed to be solvable quickly while still creating meaningful conflicts between a greedy baseline and RAILMIND.
________________________________________
53. Baseline Scheduler
RAILMIND must be compared against a baseline.
Recommended baseline:
Greedy Earliest-Feasible Scheduler
Algorithm:
Sort tasks by priority
       ↓
Select earliest feasible window
       ↓
Assign available resource
       ↓
Continue until all tasks processed
Compare:
RAILMIND
vs
Greedy baseline
Metrics:
•	train delay
•	maintenance completion
•	unscheduled critical tasks
•	block count
•	conflicts
•	overrun probability
•	recovery performance
________________________________________
54. Frontend Application Architecture
src/
│
├── app/
│
├── components/
│   ├── command-center/
│   ├── maintenance/
│   ├── blocks/
│   ├── trains/
│   ├── simulation/
│   ├── disruptions/
│   ├── recommendations/
│   └── common/
│
├── features/
│   ├── planning/
│   ├── optimization/
│   ├── scenarios/
│   ├── recovery/
│   └── approvals/
│
├── services/
│   └── api/
│
├── hooks/
├── stores/
├── types/
└── utils/
________________________________________
55. Primary UI Screens
1. Command Center
Shows:
•	network health
•	active blocks
•	delayed trains
•	critical maintenance
•	active disruptions
•	recommendations
2. Maintenance Workspace
Shows:
•	maintenance queue
•	priority
•	risk
•	overdue tasks
•	predicted duration
•	recommended windows
3. Block Planning Workspace
Shows:
•	candidate blocks
•	conflicts
•	train impact
•	resources
•	bundling
4. Plan Comparison
Plan A
Plan B
Plan C
with:
•	delay
•	risk
•	maintenance completion
•	block count
5. Simulation Workspace
What-if controls.
6. Disruption Workspace
Incident → impact → recovery.
7. Approval Workspace
Recommendation
↓
Evidence
↓
Alternatives
↓
Approve / Modify / Reject
________________________________________
56. Recommended Frontend State Management
Use:
TanStack Query
for server state.
Use lightweight client state such as:
Zustand
for:
•	selected scenario
•	UI state
•	filters
•	comparison mode
Do not duplicate backend domain state unnecessarily in the browser.
________________________________________
57. Container Architecture
Tier 1:
Docker Compose

┌───────────────────────┐
│ frontend              │
│ Next.js               │
└──────────┬────────────┘
           │
┌──────────▼────────────┐
│ backend               │
│ FastAPI               │
└──────────┬────────────┘
           │
     ┌─────┴──────┐
     ▼            ▼
PostgreSQL      Worker
+ PostGIS       Optimization
                Simulation
                ML
Optional:
Redis
________________________________________
58. Production Evolution
The same logical architecture can later become:
API Gateway
      │
      ├── State Service
      ├── Maintenance Service
      ├── Planning Service
      ├── ML Service
      ├── Optimization Service
      ├── Simulation Service
      ├── Event Service
      ├── Decision Service
      └── Audit Service
             │
          Kafka
             │
      PostgreSQL/PostGIS
             │
       Data Lake / Warehouse
This is a future extraction—not the SIH implementation.
________________________________________
59. Kubernetes Roadmap
When RAILMIND reaches pilot/enterprise scale:
Kubernetes
│
├── API Deployment
├── Worker Deployment
├── ML Inference Deployment
├── Optimization Worker Pool
├── Simulation Worker Pool
├── Event Consumers
└── Observability Stack
Horizontal scaling can then be applied to stateless workloads; Kubernetes HPA supports scaling workloads based on resource or custom metrics.
________________________________________
60. Model Serving Evolution
Tier 1:
Python process
Tier 2:
Dedicated ML inference service
Tier 3:
Potential:
MLflow
Model Registry
Dedicated inference workers
GPU-backed models where justified
Do not introduce MLflow/Kubernetes/GPU infrastructure simply to make the MVP look enterprise-grade.
The architecture must be enterprise-ready; the implementation does not need enterprise-scale infrastructure yet.
________________________________________
61. CI/CD
Recommended:
GitHub
   ↓
GitHub Actions
   ↓
Lint
   ↓
Unit Tests
   ↓
Integration Tests
   ↓
Build Docker Image
   ↓
Security Scan
   ↓
Deploy
Quality tools:
Python
•	Ruff
•	Black
•	MyPy
•	Pytest
Frontend
•	ESLint
•	Prettier
•	TypeScript
•	Vitest
•	Playwright
________________________________________
62. Testing Strategy
RAILMIND requires multiple testing levels.
Unit Testing
Test:
•	rules
•	scoring
•	ML preprocessing
•	objective calculations
•	state transitions
Integration Testing
Test:
API
+
Database
+
Optimizer
+
Simulation
Optimization Testing
Create tiny hand-verifiable scenarios.
Example:
2 tasks
2 windows
1 train conflict
Expected solution should be manually known.
Simulation Testing
Verify:
same seed → same result
Recovery Testing
Test:
normal plan
→ overrun
→ invalidation
→ recovery
End-to-End
Test the entire:
Sense
→ Predict
→ Plan
→ Optimize
→ Simulate
→ Approve
→ Disrupt
→ Recover
loop.
________________________________________
63. Safety Architecture
RAILMIND must never directly control:
•	trains
•	signals
•	interlocking
•	safety-critical railway equipment
The system produces decision support.
Execution remains inside authorized railway workflows.
This is consistent with the blueprint’s explicit boundary that RAILMIND is not an autonomous controller and that safety constraints cannot be traded for efficiency.
________________________________________
64. Failure Boundaries
The following components must be isolated logically:
Prediction
Optimization
Simulation
Execution
A prediction failure must not automatically trigger execution.
A simulation result must not directly modify live state.
A scenario must not modify live state.
An LLM response must not modify live state.
Only an authorized approval action can transition a recommendation toward execution.
________________________________________
65. Configuration Architecture
Do not hard-code:
objective weights
priority weights
Monte Carlo count
solver timeout
planning horizon
risk thresholds
delay thresholds
Store them in configuration.
Example:
optimization:
  timeout_seconds: 10

objective:
  train_delay: 5
  maintenance_priority: 4
  block_count: 1
  overrun_risk: 2
  bundling: 1

simulation:
  monte_carlo_runs: 200

planning:
  horizon_hours: 72
This is especially important because the blueprint identifies these assumptions as configuration values that should be tuned once real domain data becomes available.
________________________________________
66. Versioning Strategy
Use semantic versions:
API:
v1

ML:
duration-model@1.0.0

Rules:
constraints@1.2.0

Objective:
objective@1.0.0

Dataset:
synthetic-corridor@1.0.0
Every optimization run stores all versions.
________________________________________
67. Reproducibility Contract
An optimization result must be reproducible using:
state_version
+
dataset_version
+
model_versions
+
constraint_version
+
objective_weights
+
solver_version
+
random_seed
Therefore:
OptimizationRun
        ↓
Reconstruct Input
        ↓
Re-run
        ↓
Compare Result
________________________________________
68. Data Lifecycle
Raw Data
   ↓
Validation
   ↓
Canonicalization
   ↓
Operational Store
   ↓
Feature Generation
   ↓
Prediction
   ↓
Optimization
   ↓
Decision
   ↓
Execution
   ↓
Actual Outcome
   ↓
Historical Store
   ↓
Future Model Training
This creates the eventual learning loop.
________________________________________
69. Technical KPIs
Optimization
•	solve time
•	feasibility rate
•	objective score
•	number of conflicts
•	maintenance completion
ML
•	MAE
•	RMSE
•	F1
•	calibration
•	confidence
Operations
•	predicted delay
•	actual delay
•	overrun probability
•	recovery time
•	asset availability
Product
•	approval time
•	recommendation acceptance rate
•	scenario usage
•	planner interaction time
________________________________________
70. MVP Definition of Done
RAILMIND Tier 1 is technically complete when:
Data
•	corridor loads
•	stations load
•	sections load
•	assets load
•	maintenance tasks load
•	trains load
•	resources load
Intelligence
•	priority model works
•	duration model works
•	delay model works
•	risk model works
Planning
•	candidate windows generated
•	tasks assigned
•	resources assigned
•	bundling works
•	train impact calculated
Optimization
•	CP-SAT works
•	hard constraints enforced
•	objective works
•	alternatives generated
Simulation
•	baseline simulation works
•	what-if works
•	Monte Carlo works
Disruption
•	block overrun works
•	track unavailable works
•	recovery plan generated
Governance
•	authentication
•	RBAC
•	approval
•	audit
•	state versioning
UI
•	command center
•	planning workspace
•	simulation workspace
•	disruption workspace
•	recommendation workspace
Demonstration
The complete sequence must work:
LOAD
 ↓
PRIORITIZE
 ↓
PREDICT
 ↓
GENERATE BLOCKS
 ↓
OPTIMIZE
 ↓
SIMULATE
 ↓
COMPARE
 ↓
APPROVE
 ↓
BLOCK OVERRUN
 ↓
UPDATE STATE
 ↓
RECOVER
 ↓
APPROVE RECOVERY
________________________________________
71. Recommended Final Architecture
The actual SIH deployment should therefore be:
                    RAILMIND MVP
                         │
             ┌───────────┴───────────┐
             │                       │
          Frontend                Backend
       Next.js/React             FastAPI
             │                       │
             │         ┌─────────────┼─────────────┐
             │         │             │             │
             │       State          ML           Rules
             │       Engine       Engine        Engine
             │         │             │             │
             │         └─────────────┼─────────────┘
             │                       │
             │                 Optimization
             │                  OR-Tools
             │                       │
             │                   Simulation
             │                       │
             │                 Monte Carlo
             │                       │
             │               Decision Intelligence
             │                       │
             └───────────────────────┤
                                     │
                              PostgreSQL
                                  + PostGIS
                                     │
                                  Redis
                                 optional
________________________________________
72. Technology Stack — Final Lock
Layer	Technology	MVP	Future
Frontend	React	✓	✓
Framework	Next.js	✓	✓
Language	TypeScript	✓	✓
UI	Tailwind + shadcn	✓	✓
Backend	Python	✓	✓
API	FastAPI	✓	✓
Validation	Pydantic	✓	✓
ORM	SQLAlchemy	✓	✓
Database	PostgreSQL	✓	✓
Spatial	PostGIS	✓	✓
ML	scikit-learn	✓	✓
ML	XGBoost	✓	✓
Optimization	OR-Tools CP-SAT	✓	✓
Graph	NetworkX	✓	✓
Simulation	Python/SimPy	✓	Advanced
Monte Carlo	NumPy	✓	✓
Queue	Redis	Optional	✓
Messaging	In-process	✓	—
Messaging	Kafka/Redpanda	—	✓
Containers	Docker	✓	✓
Orchestration	Docker Compose	✓	—
Orchestration	Kubernetes	—	✓
Logging	Structured JSON	✓	✓
Observability	Basic metrics	✓	—
Observability	OpenTelemetry	—	✓
Metrics	Prometheus	—	✓
Dashboards	Grafana	—	✓
Identity	JWT/RBAC	✓	Enterprise SSO
GIS	Basic corridor view	✓	MapLibre/Deck.gl
GNN	—	—	Phase 2+
Graph DB	—	—	Only if justified
LLM	Optional	Optional	Optional
________________________________________
73. Model Count — Final Recommendation
The first RAILMIND implementation should contain:
4 ML models
+
1 deterministic rules/scoring layer
+
1 CP-SAT optimization engine
+
1 simulation engine
+
1 Monte Carlo robustness engine
+
1 graph propagation engine
Specifically:
MODEL 01
Maintenance Priority

MODEL 02
Maintenance Duration

MODEL 03
Train Delay

MODEL 04
Asset Failure Risk
Do not build:
5+ random AI models
GNN
LLM decision-maker
reinforcement learning
computer vision
deep learning
autonomous agent swarm
for the MVP merely because they sound advanced.
The sophistication of RAILMIND comes from how the models, rules, optimizer, simulation and state engine interact, not from the number of neural networks.
________________________________________
74. Future Technical Evolution
Phase 0 — SIH
Modular Monolith
+
4 ML Models
+
CP-SAT
+
Simulation
+
Monte Carlo
+
State Engine
Phase 1 — Pilot
Real Railway Data
+
Adapters
+
Redis
+
Workers
+
Observability
+
Advanced RBAC
Phase 2 — Adaptive Intelligence
GNN
+
Event Streaming
+
Continuous Replanning
+
Advanced Delay Propagation
Phase 3 — Multi-Division
Kubernetes
+
Distributed Workers
+
Multi-Corridor Optimization
+
Resource Optimization
+
Advanced Digital Twin
Phase 4 — Railway Intelligence Platform
Weather Intelligence
+
Energy Optimization
+
Freight Intelligence
+
Continuous Learning
+
Enterprise Governance
This follows the blueprint’s roadmap from bounded SIH implementation through pilot, adaptive intelligence, multi-division operation and eventual railway intelligence platform.
________________________________________
75. Final Engineering Decision
The most important architectural decision for RAILMIND is:
Do not build a small prototype with a large-system diagram. Build a small implementation of a large-system architecture.
That means the MVP will be physically small:
1 deployment
1 database
1 backend
1 frontend
1 worker
4 ML models
1 optimizer
1 simulator
but logically it already contains the boundaries required for:
multiple divisions
multiple corridors
real railway integrations
event streaming
distributed workers
advanced ML
enterprise governance
The Tier-1 architecture therefore remains intentionally modular, with explicit interfaces around prediction, optimization, simulation and explanation so individual components can later be replaced or extracted without redesigning the orchestration layer.
Core RAILMIND engineering rule
ML predicts.
Rules constrain.
CP-SAT optimizes.
Simulation validates.
Monte Carlo measures uncertainty.
State Engine remembers reality.
Decision Intelligence explains.
Humans authorize.
That is the technical architecture that makes RAILMIND substantially more credible than a typical “AI railway scheduler” project.
