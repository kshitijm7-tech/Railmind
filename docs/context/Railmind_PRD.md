RAILMIND
Railway Maintenance, Operations & Block Intelligence Platform
Product Requirements Document — PRD v1.0
Team: Sudo Vyom
Primary Problem Statement: SIH26027 — AI-Powered Automatic Block Planning to Maximize Asset Availability for Train Operations on Indian Railways
Ministry: Ministry of Railways
Product: RAILMIND
Document Type: Product Requirements Document
Version: 1.0
Status: Build-Ready Product Specification
Scope: Tier 1 — SIH MVP
Product Posture: Production-shaped railway decision-intelligence platform
________________________________________
1. Document Purpose
This Product Requirements Document defines the product requirements for RAILMIND, a railway decision-intelligence platform designed to coordinate maintenance planning with train operations while continuously adapting to changes in the operational environment.
The PRD translates the RAILMIND solution and architecture blueprint into:
•	Product goals
•	User problems
•	Personas
•	User journeys
•	Functional requirements
•	AI/ML requirements
•	Optimization requirements
•	Simulation requirements
•	Disruption and recovery requirements
•	Human-in-the-loop requirements
•	UI/UX requirements
•	Data requirements
•	Governance requirements
•	Non-functional requirements
•	MVP boundaries
•	Acceptance criteria
•	Success metrics
•	Roadmap requirements
The central product principle is:
RAILMIND does not optimize a static railway schedule. It continuously optimizes decisions against a changing railway state.
________________________________________
2. Product Identity
2.1 Product Name
RAILMIND
Working expansion
Railway Maintenance, Operations & Block Intelligence Platform
________________________________________
3. Product Vision
RAILMIND aims to become an adaptive railway decision-intelligence platform that helps railway personnel coordinate:
•	Maintenance work
•	Infrastructure availability
•	Maintenance blocks / possessions
•	Train operations
•	Resources
•	Operational constraints
•	Disruptions
•	Recovery plans
within one continuously updated decision environment.
The immediate entry point is SIH26027 and automatic maintenance block planning.
The larger product vision is a railway intelligence platform capable of continuously understanding railway state, predicting risks, generating feasible plans, evaluating alternatives, supporting human decisions and adapting when reality diverges from the original plan.
________________________________________
4. Core Product Proposition
“Make every railway maintenance block count — while continuously adapting to the railway as it actually operates.”
RAILMIND is not simply a scheduling algorithm.
It is a closed-loop decision system:
Sense → Understand → Predict → Plan → Optimize → Simulate → Decide → Execute → Observe → Recover → Re-plan
The system combines:
•	Machine learning for prediction
•	Deterministic rules for hard constraints
•	Constraint optimization for planning
•	Simulation for consequence evaluation
•	Decision intelligence for ranking alternatives
•	Human approval for material decisions
________________________________________
5. Problem Statement
5.1 Core Problem
Railway maintenance requires infrastructure access, while train operations require that same infrastructure to remain available.
Maintenance activities can therefore conflict with:
•	Train movements
•	Other maintenance activities
•	Resource availability
•	Infrastructure constraints
•	Departmental requirements
•	Maintenance deadlines
•	Asset criticality
Furthermore, railway operations are dynamic.
A plan that is feasible at 10:00 may become invalid at 10:30 because:
•	A maintenance task overruns
•	A train is delayed
•	A track becomes unavailable
•	An asset fails
•	A resource becomes unavailable
•	A high-priority train is introduced
•	A planned block is cancelled
Traditional static planning therefore struggles with operational uncertainty.
________________________________________
6. Product Problem Decomposition
Problem	RAILMIND Capability
Important maintenance is poorly prioritized	Maintenance Intelligence
Maintenance windows conflict with trains	Block Intelligence
Multiple departments request separate blocks	Task Bundling
Blocks create direct/downstream delay	Train Coordination
Maintenance duration is uncertain	Duration Prediction
Plans become invalid after disruption	State Reconciliation
Track/infrastructure suddenly becomes unavailable	Disruption Intelligence
Recovery requires manual re-planning	Recovery Intelligence
Users cannot understand why a plan was selected	Explainable Decision Intelligence
Different teams work from fragmented information	Shared Railway State
________________________________________
7. Product Goals
7.1 Primary Goals
RAILMIND must:
1.	Represent a bounded railway corridor digitally.
2.	Represent infrastructure, assets, trains, maintenance tasks and resources.
3.	Prioritize maintenance tasks.
4.	Identify compatible maintenance activities.
5.	Generate candidate maintenance blocks.
6.	Coordinate blocks with train operations.
7.	Generate feasible optimized plans.
8.	Evaluate plans before approval.
9.	Quantify uncertainty and overrun risk.
10.	Detect plan deviations.
11.	Re-plan after disruptions.
12.	Provide ranked recovery alternatives.
13.	Explain recommendations.
14.	Require authorized human approval.
15.	Maintain an auditable decision history.
________________________________________
8. Product Non-Goals
For the SIH MVP, RAILMIND will NOT:
•	Control trains autonomously.
•	Control signals autonomously.
•	Control safety-critical railway equipment.
•	Replace TMS, SMMS, TDMS, BDMS or other systems of record.
•	Optimize the entire Indian railway network.
•	Optimize multiple divisions at national scale.
•	Require production railway integrations.
•	Deploy a large microservices architecture.
•	Depend on a GNN for the core demonstration.
•	Use deep learning merely for novelty.
•	Claim production deployment where only synthetic data exists.
________________________________________
9. Product Scope
9.1 Tier 1 — SIH MVP
Must Build
•	Bounded corridor
•	Railway network model
•	Asset model
•	Maintenance backlog
•	Train timetable
•	Resource pools
•	Maintenance priority scoring
•	Duration prediction
•	Delay prediction
•	Candidate block generation
•	Cross-department task bundling
•	Train-block coordination
•	CP-SAT optimization
•	Scenario simulation
•	Monte Carlo robustness analysis
•	Block overrun handling
•	Track unavailable disruption
•	Recovery optimization
•	Recommendation engine
•	Explanation engine
•	Human approval workflow
•	Audit trail
•	Command center
•	Planning workspace
•	Simulation workspace
•	Disruption workspace
________________________________________
9.2 Tier 2 — Pilot
Future requirements include:
•	Real historical railway data
•	Real integration adapters
•	Event-driven architecture
•	Multi-division planning
•	Advanced governance
•	Model monitoring
•	Production observability
•	Deeper role-based permissions
•	Advanced delay propagation
________________________________________
9.3 Tier 3 — Platform Vision
Future platform capabilities may include:
•	Multi-zone optimization
•	Resource optimization
•	Energy optimization
•	Freight optimization
•	Weather intelligence
•	Continuous learning
•	Advanced digital twin
•	Enterprise security
•	Large-scale graph intelligence
________________________________________
10. Target Users
10.1 Operations Manager
Needs
•	Network-level visibility
•	Operational trade-offs
•	Plan comparison
•	Disruption overview
RAILMIND Value
Provides a decision command center showing:
•	Current state
•	Planned blocks
•	Maintenance risk
•	Train impact
•	Conflicts
•	Recovery options
________________________________________
11. Traffic / Operations Controller
Needs
•	Efficient train movement
•	Awareness of active blocks
•	Immediate disruption impact
•	Recovery options
RAILMIND Value
Provides:
•	Affected trains
•	Predicted delays
•	Conflicts
•	Alternative sequencing
•	Recovery recommendations
________________________________________
12. Engineering Planner
Needs
•	Complete maintenance efficiently
•	Identify suitable block windows
•	Coordinate maintenance activities
RAILMIND Value
Provides:
•	Prioritized maintenance queue
•	Candidate windows
•	Task bundling
•	Duration estimates
•	Risk indicators
•	Recommended blocks
________________________________________
13. S&T / TRD Planner
Needs
•	Coordinate department-specific work
•	Share infrastructure possession
•	Reduce duplicate access windows
RAILMIND Value
Provides cross-department bundling opportunities.
________________________________________
14. Maintenance Supervisor
Needs
•	Realistic maintenance windows
•	Crew availability
•	Task duration uncertainty
•	Readiness information
RAILMIND Value
Provides:
•	Expected duration
•	P10/P90 duration
•	Crew requirements
•	Readiness
•	Overrun risk
________________________________________
15. Asset Manager
Needs
•	Asset availability
•	Asset criticality
•	Maintenance risk
•	Failure prevention
RAILMIND Value
Provides:
•	Asset condition
•	Criticality
•	Failure risk
•	Maintenance backlog
•	Dependency information
________________________________________
16. Senior Decision Maker
Needs
•	Understand trade-offs
•	Compare alternatives
•	Approve/reject recommendations
RAILMIND Value
Provides:
•	Ranked plans
•	Impact comparison
•	Explanation
•	Risks
•	Alternatives
•	Approval workflow
________________________________________
17. Product Operating Principle
RAILMIND follows a strict responsibility separation:
Component	Responsibility
ML	Predict what is likely to happen
Rules Engine	Define what must never be violated
Optimizer	Find the best feasible plan
Simulator	Determine what could happen
Decision Engine	Rank feasible alternatives
Human	Decide what should actually happen
This is a core safety and product principle.
No AI model may independently authorize safety-critical execution.
________________________________________
18. Core Product Workflow
18.1 Closed-Loop Workflow
Step 1 — Sense
Collect:
•	Railway state
•	Maintenance requests
•	Train schedules
•	Asset status
•	Resource status
•	Events
Step 2 — Understand
Construct the current railway state.
Identify:
•	Dependencies
•	Conflicts
•	Available infrastructure
•	Planned blocks
•	Affected trains
Step 3 — Predict
Generate:
•	Maintenance duration
•	Delay predictions
•	Failure risk
•	Priority score
•	Uncertainty estimates
Step 4 — Plan
Generate:
•	Candidate maintenance windows
•	Candidate blocks
•	Bundling opportunities
Step 5 — Optimize
Apply:
•	Hard constraints
•	Soft objectives
•	Train impact
•	Maintenance priorities
•	Resource availability
•	Robustness considerations
Step 6 — Simulate
Evaluate:
•	Baseline
•	Candidate plans
•	Alternative plans
•	Overrun scenarios
•	Disruption scenarios
Step 7 — Decide
Present:
•	Recommended plan
•	Alternatives
•	Expected impact
•	Risks
•	Explanation
Step 8 — Approve
Authorized user:
•	Approves
•	Modifies
•	Rejects
Step 9 — Execute
Approved decisions move into the appropriate authorized railway workflow.
Step 10 — Observe
Compare:
PLAN vs ACTUAL
Step 11 — Recover
If significant deviation occurs:
•	Identify affected components
•	Recalculate impact
•	Generate recovery alternatives
Step 12 — Re-plan
Optimize again using the updated railway state.
________________________________________
19. Core Product Modules
RM-CORE — Core Platform
Responsibilities:
•	Authentication
•	User identity
•	RBAC
•	Configuration
•	Audit
•	State/version management
________________________________________
RM-AI — Maintenance Intelligence
Responsibilities:
•	Maintenance priority
•	Asset risk
•	Duration prediction
•	Task readiness
•	Task grouping
________________________________________
RM-BLOCK — Block Intelligence
Responsibilities:
•	Candidate window generation
•	Block feasibility
•	Block scheduling
•	Block utilization
________________________________________
RM-COORD — Coordination Engine
Responsibilities:
•	Cross-department bundling
•	Shared possession identification
•	Resource coordination
________________________________________
RM-TRAIN — Train Coordination
Responsibilities:
•	Affected train detection
•	Delay estimation
•	Sequencing
•	Holding
•	Timing alternatives
•	Downstream impact
________________________________________
RM-OPT — Optimization Engine
Responsibilities:
•	Constraint modeling
•	Block assignment
•	Task scheduling
•	Train coordination
•	Recovery optimization
Technology target:
Google OR-Tools CP-SAT
________________________________________
RM-SIM — Simulation Engine
Responsibilities:
•	What-if scenarios
•	Plan comparison
•	Delay propagation
•	Duration uncertainty
•	Monte Carlo robustness
________________________________________
RM-DISRUPT — Disruption Intelligence
Responsibilities:
•	Incident classification
•	Dependency analysis
•	Plan invalidation
•	Impact analysis
•	Recovery candidate generation
________________________________________
RM-DECIDE — Decision Intelligence
Responsibilities:
•	Candidate ranking
•	Objective breakdown
•	Alternative ranking
•	Recommendation generation
________________________________________
RM-XAI — Explainability
Responsibilities:
•	Recommendation rationale
•	Constraint trace
•	Objective breakdown
•	Evidence
•	Alternatives
•	Confidence
________________________________________
RM-APPROVAL — Human Decision Workflow
Responsibilities:
•	Review
•	Approve
•	Modify
•	Reject
•	Record decision
________________________________________
RM-CMD — Command Center
Responsibilities:
•	Network overview
•	Current railway state
•	Active blocks
•	Planned blocks
•	Maintenance risk
•	Train impact
•	Alerts
________________________________________
20. Canonical Domain Model
RAILMIND must maintain a canonical representation independent of source-system schemas.
Core entities:
RailwayNetwork
Contains:
•	Zone
•	Division
•	Sections
•	Stations
•	Tracks
•	Infrastructure
•	Assets
Section
Attributes:
•	section_id
•	from_station
•	to_station
•	length
•	track count
•	maximum speed
•	department owners
•	criticality
Asset
Types:
•	Track asset
•	Signal asset
•	OHE asset
•	Bridge
•	Electrical asset
MaintenanceTask
Contains:
•	Task ID
•	Section
•	Department
•	Task type
•	Duration
•	Duration uncertainty
•	Crew requirement
•	Qualification
•	Criticality
•	Overdue days
•	Dependencies
•	Earliest start
•	Latest finish
Train
Contains:
•	Train ID
•	Train type
•	Priority
•	Route
•	Section sequence
•	Scheduled timings
Resource
Contains:
•	Department
•	Crew availability
•	Shift
•	Equipment
•	Machinery
Block
Contains:
•	Block ID
•	Section
•	Start time
•	End time
•	Assigned tasks
•	Status
•	Plan version
Incident
Types:
•	Asset failure
•	Track damage
•	External disruption
Recommendation
Contains:
•	Recommendation ID
•	State version
•	Plan version
•	Model version
•	Recommended action
•	Expected outcome
•	Affected trains
•	Affected maintenance
•	Affected resources
•	Constraint trace
•	Objective breakdown
•	Alternatives
•	Evidence
Outcome
Contains:
•	Actual execution result
•	Predicted outcome
•	Actual outcome
•	Deviation
•	Decision history
________________________________________
21. Demo Dataset Requirements
The SIH MVP shall use a bounded synthetic but rigorously structured dataset.
Target configuration
Parameter	MVP Value
Division	1
Line	Single line
Stations	6
Track sections	9
Planning horizon	72 hours
Train services	48
Passenger trains	34
Goods trains	14
Maintenance tasks	22
Overdue tasks	3
Critical tasks	4
Departments	4
Block windows	4–6 per section/day
Shifts	2
Crew per shift	3–6
Scripted overrun	+45 minutes
Track disruption	1
These values are configurable assumptions rather than permanent production constants.
________________________________________
22. Maintenance Intelligence Requirements
FR-MI-001 — Maintenance Priority
The system shall calculate a priority score for every maintenance task.
Priority shall consider:
•	Criticality
•	Overdue days
•	Asset failure risk
•	Safety relevance
•	Downstream operational impact
Default weighting
•	Criticality: 30%
•	Overdue: 20%
•	Failure risk: 20%
•	Safety flag: 20%
•	Downstream impact: 10%
Weights shall be configurable.
________________________________________
23. Duration Prediction
The system shall estimate maintenance duration.
Inputs
•	Task type
•	Department
•	Asset type
•	Section criticality
•	Crew size
•	Historical duration
•	Time of day
•	Similar-task history
Output
•	Expected duration
•	P10 duration
•	P90 duration
•	Overrun risk
Model
Initial target:
XGBoost / gradient-boosted regression
The model must not directly make scheduling decisions.
________________________________________
24. Train Delay Prediction
The system shall estimate train impact for proposed maintenance blocks.
Inputs
•	Block window
•	Section
•	Affected trains
•	Train priority
•	Historical delay patterns
•	Time of day
Outputs
•	Direct train delay
•	Confidence
•	Downstream delay estimate
Initial cascading approach:
NetworkX graph propagation
A GNN may be evaluated later as a stretch enhancement.
________________________________________
25. Block Planning Requirements
FR-BLOCK-001
The system shall generate feasible candidate block windows.
Each candidate shall contain:
•	Section
•	Earliest start
•	Latest end
•	Maximum duration
•	Available resources
•	Affected trains
•	Relevant constraints
________________________________________
FR-BLOCK-002
The system shall identify whether maintenance tasks can be grouped into the same block.
________________________________________
FR-BLOCK-003
The system shall identify compatible cross-department maintenance tasks.
________________________________________
FR-BLOCK-004
The system shall calculate expected operational impact for every candidate block.
________________________________________
26. Optimization Requirements
RAILMIND shall use a constraint optimization engine to generate feasible plans.
26.1 Decision Variables
The optimization model shall represent:
•	Task-to-window assignment
•	Window activation
•	Block start/end
•	Train delay
•	Unscheduled tasks
________________________________________
27. Hard Constraints
The optimizer shall never violate:
1.	Safety constraints
2.	Possession constraints
3.	Infrastructure availability
4.	Maintenance duration requirements
5.	Task dependencies
6.	Resource availability
7.	Crew qualification
8.	Section exclusivity
9.	Train movement constraints
10.	Window bounds
11.	Deadlines
12.	Authorized railway policy constraints
________________________________________
28. Optimization Objectives
The optimizer shall attempt to:
1.	Minimize train delay.
2.	Minimize high-priority unscheduled maintenance.
3.	Minimize block fragmentation.
4.	Minimize overrun risk.
5.	Maximize cross-department bundling.
The default objective weights shall remain configurable.
________________________________________
29. Plan Comparison
For each optimization run, RAILMIND should produce:
•	Recommended plan
•	Alternative plans
•	Total expected delay
•	Number of affected trains
•	Maintenance completion
•	Number of blocks
•	Overrun risk
•	Constraint status
•	Objective score
The user must be able to compare plans.
________________________________________
30. Robustness Requirements
A schedule should not be evaluated only under perfect assumptions.
RAILMIND shall perform a simplified Monte Carlo robustness analysis.
Tier 1 target
200 simulation draws
Maintenance duration shall be sampled from the configured uncertainty range.
The system shall report:
•	Probability of block overrun
•	Probability of plan violation
•	Risk by block
•	Overall robustness
This enables comparison such as:
Plan A: lower delay, higher overrun risk
Plan B: slightly higher delay, lower overrun risk
________________________________________
31. Simulation Requirements
The RAILMIND digital twin is computational rather than a 3D visualization.
It shall maintain:
•	Network state
•	Train state
•	Block state
•	Maintenance state
•	Resource state
All simulation scenarios shall use the same canonical model as the optimizer.
________________________________________
32. What-If Engine
Users shall be able to create scenario branches without changing live state.
Supported scenarios:
Scenario A — Duration Overrun
Example:
Maintenance takes 30/60/120 minutes longer.
Scenario B — Block Cancellation
A planned block becomes unavailable.
Scenario C — Priority Train
A high-priority train is introduced.
Scenario D — Infrastructure Loss
A track section becomes unavailable.
Scenario E — Resource Loss
A crew or equipment resource becomes unavailable.
Scenario F — Window Change
A preferred maintenance window changes.
Scenario G — Train Delay
A train arrives later than planned.
________________________________________
33. Scenario Isolation
Every scenario must operate as a copy-on-write state branch.
A scenario must NEVER mutate the live operational state.
Each scenario shall return:
•	Total delay
•	Affected trains
•	Affected blocks
•	Maintenance completion
•	Risk profile
________________________________________
34. Disruption Intelligence
RAILMIND shall treat disruption as a first-class product workflow.
34.1 Block Overrun
Flow:
Active Block → Actual Duration Increases → BLOCK_OVERRUN Event → State Update → Identify Affected Trains → Predict Delay → Re-optimize → Simulate → Rank → Recommend → Human Approval
Only the affected region and downstream windows should be re-solved where possible.
________________________________________
35. Track Unavailability
When:
TRACK_UNAVAILABLE
is triggered:
1.	Classify incident.
2.	Identify affected section.
3.	Update railway state.
4.	Invalidate dependent plans.
5.	Identify affected trains.
6.	Identify affected blocks.
7.	Identify affected maintenance.
8.	Generate recovery candidates.
9.	Re-solve optimization.
10.	Simulate candidates.
11.	Rank alternatives.
12.	Explain recommendation.
13.	Present to authorized human.
14.	Record decision.
15.	Monitor recovery.
________________________________________
36. Recovery Intelligence
Recovery is not a separate scheduling engine.
The same optimization framework shall be reused with updated state.
Potential recovery actions include:
•	Reschedule maintenance
•	Move block
•	Hold train
•	Resequence train
•	Reassign available resources
•	Remove unavailable sections from candidate windows
________________________________________
37. Railway State Model
RAILMIND shall maintain four explicit state categories.
PLAN
What was intended.
ACTUAL
What is currently happening.
PREDICTION
What the system expects to happen.
SCENARIO
What could happen under a simulated assumption.
These states must remain logically separated.
________________________________________
38. State Versioning
Every material state change shall create a new state version.
Example:
v1021 → v1022 → v1023
Every optimization and recommendation must reference the exact state version used to produce it.
This enables:
•	Reproducibility
•	Auditability
•	Debugging
•	Decision reconstruction
________________________________________
39. Explainability Requirements
Every material recommendation shall answer:
Why this block?
Why was this maintenance window selected?
Why this time?
Why is this time better than other feasible windows?
Why these tasks together?
Why can the tasks share the same possession?
What trains are affected?
Which services experience impact?
Why not the alternatives?
Why were alternative plans ranked lower?
What constraints mattered?
Which constraints shaped the result?
What happens if the plan overruns?
What recovery consequences exist?
________________________________________
40. Recommendation Evidence
Every recommendation should expose structured evidence:
•	State version
•	Plan version
•	Model version
•	Recommended action
•	Expected outcome
•	Affected trains
•	Affected maintenance
•	Affected resources
•	Constraint trace
•	Objective breakdown
•	Top alternatives
•	Prediction evidence
•	Confidence/risk
The explanation layer should render this structured evidence into human-readable language.
________________________________________
41. LLM / Copilot Requirements
An LLM may optionally support:
•	Natural-language querying
•	Recommendation explanation
•	Scenario explanation
•	Data interpretation assistance
The LLM must NOT:
•	Override constraints
•	Generate its own safety decisions
•	Invent railway state
•	Invent train information
•	Directly control railway systems
•	Replace the optimizer
•	Replace human approval
The structured system remains authoritative.
________________________________________
42. Human-in-the-Loop Workflow
Every material recommendation must pass through:
Generate → Simulate → Recommend → Review → Approve / Modify / Reject
Only authorized personnel may approve.
________________________________________
43. Approval Requirements
The approval interface shall display:
•	Recommended plan
•	Impact
•	Risk
•	Alternatives
•	Constraints
•	Explanation
•	Confidence
•	State version
User actions:
•	Approve
•	Modify
•	Reject
•	Compare
Every action must be logged.
________________________________________
44. Role-Based Access
Tier 1 shall provide basic RBAC.
Example roles:
•	Operations Manager
•	Traffic Controller
•	Engineering Planner
•	S&T Planner
•	TRD Planner
•	Maintenance Supervisor
•	Asset Manager
•	Senior Decision Maker
•	Administrator
Permissions shall determine which workflows each user may access.
________________________________________
45. Audit Requirements
The system shall maintain an append-only audit trail.
Every material action should record:
•	User
•	Action
•	Timestamp
•	State version
•	Previous value
•	New value
•	Recommendation
•	Decision
•	Plan version
________________________________________
46. Command Center Requirements
The command center shall provide a network-level view.
Required information
•	Corridor status
•	Asset availability
•	Maintenance risk
•	Planned blocks
•	Active blocks
•	Train impact
•	Current disruptions
•	Alerts
•	Recovery status
________________________________________
47. Planning Workspace
The planning workspace shall include:
Maintenance Queue
Show:
•	Task
•	Priority
•	Criticality
•	Overdue status
•	Asset risk
•	Expected duration
•	Uncertainty
Block Opportunities
Show:
•	Candidate windows
•	Feasibility
•	Affected trains
•	Resource availability
•	Risk
Bundling
Show:
•	Compatible tasks
•	Departments
•	Shared possession opportunity
Plan Comparison
Allow:
•	Plan A
•	Plan B
•	Plan C
to be compared.
________________________________________
48. Simulation Workspace
The simulation workspace shall provide:
1.	Baseline state
2.	Scenario configuration
3.	Scenario execution
4.	Results
5.	Alternative comparison
6.	Impact visualization
7.	Risk visualization
________________________________________
49. Disruption Workspace
The disruption workspace shall display:
•	Incident
•	Affected area
•	Current impact
•	Invalidated plans
•	Affected trains
•	Affected maintenance
•	Recovery options
•	Predicted recovery
•	Approval status
•	Audit history
________________________________________
50. User Journey — Normal Planning
Planner
1.	Opens RAILMIND.
2.	Views maintenance backlog.
3.	Reviews priority scores.
4.	Selects high-priority work.
5.	System identifies compatible tasks.
6.	Planner requests planning.
7.	RAILMIND generates candidate blocks.
8.	Optimizer evaluates feasible plans.
9.	Simulation evaluates impact.
10.	Plans are ranked.
11.	Planner reviews explanation.
12.	Authorized decision-maker approves.
13.	Plan becomes the approved PLAN state.
14.	System monitors execution.
________________________________________
51. User Journey — Block Overrun
1.	Block becomes active.
2.	Actual duration increases.
3.	RAILMIND receives/creates BLOCK_OVERRUN.
4.	ACTUAL state changes.
5.	Affected trains are identified.
6.	Delay is predicted.
7.	Existing assumptions are invalidated.
8.	Optimizer generates revised plans.
9.	Simulator evaluates alternatives.
10.	Decision engine ranks them.
11.	Human reviews recommendation.
12.	Human approves/changes/rejects.
13.	Updated plan is recorded.
14.	System continues monitoring.
________________________________________
52. User Journey — Track Failure
1.	TRACK_UNAVAILABLE event occurs.
2.	Railway state updates.
3.	Dependency graph identifies affected components.
4.	Dependent plans are invalidated.
5.	Affected trains are identified.
6.	Affected maintenance tasks are identified.
7.	Recovery candidates are generated.
8.	CP-SAT re-solves updated problem.
9.	Simulation evaluates alternatives.
10.	Decision engine ranks recovery options.
11.	Human reviews.
12.	Recovery plan is approved.
13.	Decision is logged.
14.	Recovery execution is monitored.
________________________________________
53. Integration Requirements
RAILMIND shall be designed as an intelligence layer rather than a replacement system.
Potential external systems include:
•	TMS
•	SMMS
•	TDMS
•	BDMS
•	COA
•	Timetable systems
•	GIS
•	Asset registers
________________________________________
54. Tier 1 Integration
Because production railway interfaces are unavailable for the SIH cycle:
Tier 1
Use:
•	CSV
•	JSON
•	Synthetic data
•	Mock connectors
•	Simulated events
The adapter architecture must nevertheless resemble the production integration boundary.
________________________________________
55. Integration Principles
API-first
Prefer controlled APIs when available.
Event-ready
Architecture should support event-driven updates.
Batch-compatible
Support legacy/file-based ingestion.
Canonical normalization
External schemas must map into RAILMIND’s canonical model.
Read-first
Initial integrations should primarily provide decision support.
Controlled write-back
Only approved workflows should propagate decisions outward.
Graceful degradation
System must remain usable in simulation/offline mode.
________________________________________
56. Functional Requirement Priority
Priority	Meaning
P0	Absolutely required for MVP
P1	Required if core implementation permits
P2	Useful enhancement
P3	Roadmap
________________________________________
57. MVP Functional Requirements
ID	Requirement	Priority
FR-001	Load corridor	P0
FR-002	Load assets	P0
FR-003	Load maintenance tasks	P0
FR-004	Load train schedule	P0
FR-005	Load resources	P0
FR-006	Calculate maintenance priority	P0
FR-007	Predict maintenance duration	P0
FR-008	Generate candidate blocks	P0
FR-009	Bundle compatible tasks	P0
FR-010	Calculate train impact	P0
FR-011	Optimize block/train plan	P0
FR-012	Enforce hard constraints	P0
FR-013	Compare alternatives	P0
FR-014	Run simulation	P0
FR-015	Run overrun scenario	P0
FR-016	Detect track unavailability	P0
FR-017	Generate recovery plan	P0
FR-018	Explain recommendation	P0
FR-019	Human approval	P0
FR-020	Audit decision	P0
FR-021	State versioning	P0
FR-022	Command center	P0
FR-023	Planning workspace	P0
FR-024	Simulation workspace	P0
FR-025	Disruption workspace	P0
________________________________________
58. Non-Functional Requirements
NFR-001 — Optimization Performance
Target:
•	Full-horizon CP-SAT solve: <10 seconds
•	Disruption re-plan: <2 seconds
for the defined MVP dataset.
________________________________________
NFR-002 — UI Responsiveness
Browsing plans and recommendations should be sub-second for the bounded corridor dataset.
________________________________________
NFR-003 — Determinism
Demo scenarios must be deterministic and re-runnable.
Same seed should produce the same outcome.
________________________________________
NFR-004 — Reproducibility
Every recommendation must be reproducible from:
•	State version
•	Constraint version
•	Objective weights
•	Solver version
•	Model version
________________________________________
NFR-005 — Safety
Safety and hard operational constraints must never be optimized away.
________________________________________
NFR-006 — Auditability
Material decisions must be traceable.
________________________________________
NFR-007 — Explainability
Material recommendations must have structured explanations.
________________________________________
NFR-008 — Modularity
ML, optimization, simulation and explanation components must have explicit interfaces.
________________________________________
NFR-009 — Offline Capability
The MVP shall function without live railway integrations.
________________________________________
NFR-010 — Graceful Degradation
If an ML component fails, the platform should fall back to configured deterministic or baseline behavior where possible.
________________________________________
59. Technology Requirements
Frontend
React + Next.js + TypeScript
Potential visualization:
MapLibre / Deck.gl
________________________________________
Backend
Python + FastAPI + Pydantic + SQLAlchemy
________________________________________
Database
PostgreSQL + PostGIS
________________________________________
Optimization
Google OR-Tools CP-SAT
________________________________________
ML
scikit-learn / XGBoost
________________________________________
Graph
NetworkX
________________________________________
Simulation
Python discrete-event simulation + Monte Carlo
________________________________________
Messaging
Tier 1:
In-process events
Optional:
Redis
________________________________________
Deployment
Docker / Docker Compose
________________________________________
Observability
Tier 1:
•	Structured logs
•	Basic metrics
________________________________________
60. API Product Requirements
The backend API shall expose the minimum surface necessary to support the complete demonstration.
Expected capability groups:
Network
•	Get corridor
•	Get sections
•	Get stations
•	Get assets
Maintenance
•	Get tasks
•	Get prioritized tasks
•	Get task details
Planning
•	Generate candidate windows
•	Create optimization request
•	Retrieve plans
•	Compare plans
Simulation
•	Create scenario
•	Run simulation
•	Retrieve scenario results
Disruption
•	Trigger event
•	Get impact
•	Generate recovery plans
Recommendation
•	Get recommendation
•	Get explanation
•	Get alternatives
Approval
•	Approve
•	Modify
•	Reject
Audit
•	Get decision history
•	Get state history
________________________________________
61. State Transition Requirements
Example:
PLAN v1021
↓
BLOCK_ACTIVE
↓
ACTUAL v1022
↓
BLOCK_OVERRUN
↓
ACTUAL v1023
↓
PREDICTION v1023
↓
RECOVERY OPTIMIZATION
↓
SCENARIO A/B/C
↓
RECOMMENDATION R-203
↓
HUMAN APPROVAL
↓
PLAN v1024
The system should preserve the lineage.
________________________________________
62. Alert Requirements
RAILMIND should generate alerts for:
•	Critical maintenance
•	Overdue maintenance
•	Block conflict
•	High delay risk
•	High overrun risk
•	Resource conflict
•	Plan deviation
•	Block overrun
•	Track unavailable
•	Invalidated plan
•	Recovery required
________________________________________
63. Recommendation Ranking
Recommendations should be ranked according to:
1.	Hard-constraint feasibility
2.	Operational impact
3.	Maintenance priority
4.	Robustness
5.	Block efficiency
6.	Bundling benefit
Infeasible plans must never outrank feasible plans.
________________________________________
64. Baseline Comparison
The MVP should demonstrate that intelligent optimization provides value over a simpler scheduling strategy.
Candidate baseline:
Greedy / earliest-feasible scheduler
Comparison should include:
•	Train delay
•	Maintenance completion
•	Number of blocks
•	Conflict count
•	Overrun risk
The purpose is comparative demonstration, not an unsupported real-world performance claim.
________________________________________
65. Product Metrics
Asset Availability
Measure:
•	Usable asset time
•	Avoidable maintenance unavailability
________________________________________
Maintenance Efficiency
Measure:
•	Tasks completed
•	Tasks completed per block
•	Overdue reduction
•	Block utilization
________________________________________
Train Operations
Measure:
•	Total delay minutes
•	Number of affected trains
•	Delay propagation
________________________________________
Planning Quality
Measure:
•	Constraint violations
•	Feasibility
•	Re-planning success
________________________________________
Robustness
Measure:
•	Overrun performance
•	Scenario performance
•	Probability of violation
________________________________________
Recovery
Measure:
•	Recovery planning time
•	Recovery delay
•	Stabilization
________________________________________
Human Efficiency
Measure:
•	Planning time
•	Number of manual iterations
•	Recommendation overrides
________________________________________
Decision Quality
Measure:
Predicted outcome vs Actual outcome
________________________________________
66. Product Success Criteria
The Tier 1 MVP will be considered successful when it can reliably demonstrate:
Scenario 1
Maintenance backlog → priority ranking
Scenario 2
Compatible maintenance tasks → bundled possession
Scenario 3
Block generation → train impact
Scenario 4
Optimization → improved feasible plan
Scenario 5
Simulation → baseline vs alternative
Scenario 6
Human approval → auditable decision
Scenario 7
Block overrun → adaptive re-planning
Scenario 8
Track unavailable → recovery optimization
Scenario 9
Human approval → recovery execution workflow
________________________________________
67. Primary Demonstration Script
The complete MVP demonstration shall follow this sequence:
1.	Load bounded corridor.
2.	Display assets.
3.	Display maintenance backlog.
4.	AI ranks maintenance tasks.
5.	Select high-priority work.
6.	Identify compatible cross-department tasks.
7.	Generate candidate blocks.
8.	Optimize block/train plan.
9.	Display affected trains.
10.	Compare alternatives.
11.	Run simulation.
12.	Display robustness.
13.	Human approves plan.
14.	Start active block.
15.	Trigger +45-minute overrun.
16.	Detect deviation.
17.	Recalculate train impact.
18.	Generate revised plan.
19.	Trigger TRACK_UNAVAILABLE.
20.	Identify invalidated plans.
21.	Generate recovery alternatives.
22.	Simulate recovery options.
23.	Rank recovery plans.
24.	Display explanation.
25.	Human approves recovery.
26.	Record decision and outcome.
This demonstration should represent actual system behavior rather than scripted/faked outputs.
________________________________________
68. Acceptance Criteria
AC-001 — Maintenance Ranking
Given a maintenance backlog
When priority analysis runs
Then tasks must receive explainable priority scores.
________________________________________
AC-002 — Candidate Blocks
Given maintenance tasks and available windows
When block generation runs
Then feasible candidate windows must be produced.
________________________________________
AC-003 — Constraint Enforcement
Given conflicting tasks/resources/trains
When optimization runs
Then hard constraints must not be violated.
________________________________________
AC-004 — Task Bundling
Given compatible tasks from different departments
When planning runs
Then the system should identify a shared possession opportunity.
________________________________________
AC-005 — Train Impact
Given a proposed block
When impact analysis runs
Then affected trains and expected delays must be displayed.
________________________________________
AC-006 — Plan Comparison
Given multiple feasible plans
When the user opens comparison
Then impact, risk, maintenance completion and objective values must be visible.
________________________________________
AC-007 — Simulation Isolation
Given a scenario
When simulation runs
Then live operational state must remain unchanged.
________________________________________
AC-008 — Overrun Recovery
Given an active block
When a block overrun occurs
Then the system must detect the deviation and generate revised plans.
________________________________________
AC-009 — Infrastructure Disruption
Given TRACK_UNAVAILABLE
When the event is processed
Then dependent plans must be invalidated and recovery alternatives generated.
________________________________________
AC-010 — Human Approval
Given a recommendation
When an unauthorized user attempts approval
Then approval must be denied.
________________________________________
AC-011 — Auditability
Given a material decision
When it is approved/modified/rejected
Then the action must be recorded in the audit trail.
________________________________________
AC-012 — Reproducibility
Given the same state version, configuration, model and solver version
When optimization is repeated
Then the result should be reproducible under deterministic demo conditions.
________________________________________
69. Safety Requirements
RAILMIND must be designed around:
Safety before optimization.
The optimizer may trade:
•	Delay
•	Maintenance lateness
•	Block fragmentation
•	Robustness
•	Bundling
but it must never trade away hard safety or operational constraints.
________________________________________
70. AI Safety Boundary
The system shall explicitly distinguish:
Prediction
“What is likely to happen?”
Optimization
“What is the best feasible plan?”
Simulation
“What could happen?”
Decision
“What should actually happen?”
Only an authorized human is responsible for the final operational decision.
________________________________________
71. Data Quality Requirements
Every important data object should preserve:
•	Source
•	Timestamp
•	Version
•	Provenance
•	Validation state
Invalid or stale data should be identified rather than silently treated as authoritative.
________________________________________
72. Model Governance
Tier 1 shall maintain:
•	Model version
•	Prediction metadata
•	Confidence
•	Training configuration
•	Input state
•	Output state
Future versions shall add:
•	Model drift monitoring
•	Automated evaluation
•	Governance dashboards
________________________________________
73. Optimization Governance
Every optimization result must identify:
•	Solver version
•	Constraint version
•	Objective configuration
•	State version
•	Optimization timestamp
This ensures that decisions can be reconstructed.
________________________________________
74. Risk Management
Risk	Mitigation
Scope explosion	Strict Tier 1 boundary
Lack of railway data	Structured synthetic data
Incorrect optimization	Hand-checkable test cases
ML uncertainty	Confidence/risk indicators
Black-box recommendations	Structured explanation
Unsafe automation perception	Human approval
Integration unavailable	Adapter + offline mode
GNN complexity	Defer until baseline works
UI-first development	Backend decision loop first
Demo failure	Deterministic scenarios
________________________________________
75. Engineering Delivery Order
RAILMIND development should follow this sequence:
Phase 1
Lock:
•	Canonical schema
•	Dataset
•	State model
Phase 2
Build:
•	CP-SAT optimizer
independently.
Phase 3
Build:
•	Priority scoring
•	Duration prediction
•	Delay prediction
Phase 4
Connect:
Optimizer → Railway State Engine
Phase 5
Build minimum APIs.
Phase 6
Build:
•	Planning UI
•	Simulation UI
•	Disruption UI
against the actual backend.
Phase 7
Implement:
•	Overrun
•	Track unavailable
•	Recovery
Phase 8
Rehearse the complete demonstration.
Phase 9
Only after the vertical slice works:
•	GNN
•	UI polish
•	advanced Monte Carlo visualization
•	Tier 2 demonstrations
________________________________________
76. MVP Definition of Done
RAILMIND Tier 1 is considered complete only when:
☐	Corridor loads successfully
☐	Assets load successfully
☐	Maintenance tasks load
☐	Trains load
☐	Resources load
☐	Priority scoring works
☐	Duration prediction works
☐	Candidate blocks generate
☐	Bundling works
☐	Train impact works
☐	CP-SAT optimization works
☐	Hard constraints are enforced
☐	Alternative plans are generated
☐	Simulation works
☐	Monte Carlo robustness works
☐	Human approval works
☐	Audit trail works
☐	Block overrun works
☐	Track unavailable works
☐	Recovery optimization works
☐	Recommendation explanation works
☐	State versions are preserved
☐	Complete demonstration works end-to-end
________________________________________
77. Product Architecture Boundary
The product shall be structured around:
Existing Railway Systems
↓
Integration Fabric
↓
Railway Data Platform
↓
Railway State Engine
↓
ML + Rules
↓
Optimization
↓
Digital Twin / Simulation
↓
Decision Intelligence
↓
Human Approval
↓
Controlled Operational Workflow
↓
Actual Outcomes
↓
State Update
↓
Recovery / Re-plan
________________________________________
78. Product Differentiation
RAILMIND’s differentiation is not a single ML model.
The product advantage comes from combining:
1.	Railway-specific canonical state
2.	Maintenance intelligence
3.	Joint maintenance + train optimization
4.	Constraint-aware planning
5.	Uncertainty-aware scheduling
6.	Simulation
7.	Disruption recovery
8.	Continuous re-planning
9.	Explainable recommendations
10.	Human authorization
11.	Historical outcomes
12.	Integration-first architecture
________________________________________
79. Product Moat
The long-term moat can emerge from the accumulation of:
Railway State + Network Graph + Historical Plans + Constraints + Predictions + Optimization Results + Simulation Outcomes + Human Decisions + Actual Execution Outcomes
Over time this creates a railway-specific decision intelligence layer that becomes increasingly difficult to reproduce with a generic scheduling product.
________________________________________
80. Roadmap
Phase 0 — SIH MVP
Build
•	Bounded corridor
•	Maintenance intelligence
•	Block optimization
•	Train coordination
•	Simulation
•	Overrun
•	Disruption
•	Recovery
•	Explainability
•	Human approval
________________________________________
Phase 1 — Pilot
Integrate
•	Historical railway data
•	Event streams
•	Role workflows
•	Monitoring
•	Audit
•	Real validation
________________________________________
Phase 2 — Adaptive Platform
Scale intelligence
•	Event-driven planning
•	Advanced delay propagation
•	GNN experiments
•	Continuous re-planning
•	Advanced recovery
________________________________________
Phase 3 — Multi-Division
Scale network
•	Multiple corridors
•	Multiple divisions
•	Resource optimization
•	Rich digital twin
•	Cross-division coordination
________________________________________
Phase 4 — Railway Intelligence Platform
Expand decision intelligence
•	Weather
•	Energy
•	Freight
•	Broader maintenance intelligence
•	Continuous learning
•	Enterprise governance
________________________________________
81. Strategic Product Principle
RAILMIND should never become:
“An AI that tells railway operators what to do.”
Instead, it should become:
“A decision-intelligence system that understands railway state, generates feasible options, simulates consequences, explains trade-offs and helps authorized railway personnel make better decisions.”
________________________________________
82. Final Product Definition
RAILMIND is a railway decision-intelligence platform designed to coordinate maintenance blocks and train operations within a continuously changing railway environment.
It maintains a computational railway state, predicts operational and maintenance outcomes, generates feasible maintenance blocks, coordinates trains, optimizes plans, evaluates uncertainty, simulates consequences, detects disruption, generates recovery plans and presents explainable recommendations to authorized personnel.
The system does not replace railway systems of record and does not autonomously control safety-critical infrastructure.
Its central operating loop is:
Sense → Understand → Predict → Plan → Optimize → Simulate → Decide → Execute → Observe → Recover → Re-plan
For SIH26027, RAILMIND’s proof is deliberately bounded:
One corridor. Real optimization. Structured data. Real simulation. Real disruption. Real recovery. Human approval.
The MVP succeeds when it demonstrates that maintenance planning is no longer a one-time scheduling problem, but a continuous decision problem under uncertainty.
________________________________________
83. Product North Star
Make maintenance blocks intelligent.
Make railway planning resilient.
Keep the human in control.
RAILMIND
Railway Maintenance, Operations & Block Intelligence Platform
“Make every railway maintenance block count — while continuously adapting to the railway as it actually operates.”
