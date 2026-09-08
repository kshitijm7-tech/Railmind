Table of Contents

Team Sudo Vyom
RAILMIND
Railway Maintenance, Operations & Block Intelligence Platform
Consolidated Solution & Architecture Blueprint — v1.0 (Industry-Grade)
Problem Statement: SIH26027 — AI-Powered Automatic Block Planning to Maximize Asset Availability for Train Operations on Indian Railways Ministry: Ministry of Railways Document Status: Build-Ready Baseline (supersedes Blueprint v0.1 and Architecture v1.0) Document Type: Unified Product, Solution & Architecture Specification
________________________________________
Document Control
Field	Value
Product	RAILMIND
Document	Consolidated Solution & Architecture Blueprint
Version	v1.0
Supersedes	RAILMIND Ecosystem & Solution Blueprint v0.1; RAILMIND System Architecture v1.0
Primary reference	SIH26027
Product posture	Railway decision-intelligence platform; SIH is the entry point and the first production-shaped release, not a throwaway demo
Status	Build-ready — every open item from v0.1 is resolved below with either a concrete default or an explicit assumption
What changed from v0.1
This version resolves the gaps identified in review of the prior blueprint and architecture documents:
1.	A concrete optimization formulation (decision variables, constraints, objective function) replaces the earlier placeholder language (“the exact mathematical formulation should be established”).
2.	A concrete canonical data schema and demo dataset sizing replaces open-ended references to “a bounded corridor” and “synthetic data.”
3.	The two source documents are merged into one — module lists and layer lists that were duplicated across both are unified into a single architecture.
4.	Every item in the v0.1 “Open Questions” list is closed with a stated default assumption, marked [ASSUMPTION], so the team can build against it without further debate. Assumptions should be revisited once real domain input is available, but they are no longer blockers.
5.	Scope is explicitly layered: Tier 1 (build for SIH), Tier 2 (pilot-ready), Tier 3 (platform vision) — so the industry-grade ambition stays intact as roadmap and pitch material without inflating what the team commits to building this cycle.
________________________________________
PART A — PRODUCT & SOLUTION
1. Executive Summary
RAILMIND is a railway decision-intelligence platform that coordinates maintenance block planning with train operations, and continuously adapts when real-world conditions deviate from plan. The problem is not “generate a good schedule once” — it is “keep asset availability and train punctuality high under a schedule that will be disrupted.”
RAILMIND treats planning as a closed loop: Sense → Understand → Predict → Plan → Optimize → Simulate → Decide → Execute → Observe → Recover → Re-plan. Machine learning predicts (durations, delays, risk); a constraint solver decides the feasible plan; simulation evaluates consequences before commitment; and an authorized human approves every material decision. Nothing safety-critical is automated end-to-end.
For SIH26027, RAILMIND ships as a working vertical slice: a bounded corridor, a real optimization engine, real (synthetic but rigorously structured) data, and a live demonstration of plan → disruption → recovery. Everything beyond that slice is documented as roadmap, not implied as already built.
2. Core Proposition
“Make every railway maintenance block count — while continuously adapting to the railway as it actually operates.”
3. Product Thesis
The railway should not have to choose between infrastructure maintenance and reliable train operations. RAILMIND coordinates both within the constraints of a live, changing network, and is explicit about what is a prediction, what is a plan, what is happening, and what could happen — so a controlled decision-maker always knows which of those four things they are looking at.
3.1 What RAILMIND is
•	A decision-support layer over existing railway systems (TMS, SMMS, TDMS, BDMS, COA, timetable, GIS, asset registers).
•	A shared operational model of assets, infrastructure, trains, maintenance tasks, blocks, resources, constraints and events.
•	A planning engine that jointly optimizes maintenance block placement and train coordination.
•	A simulation environment for testing plans and what-if scenarios before approval.
•	An adaptive recovery system for when actual conditions diverge from plan.
•	A role-aware interface for planners, controllers, engineers and decision-makers.
3.2 What RAILMIND is not
•	Not a replacement for existing railway operational or maintenance systems of record.
•	Not an autonomous controller of trains, signals, or safety-critical infrastructure.
•	Not a dashboard, chatbot, or single ML model wearing a product’s clothing.
•	Not a claim that every railway decision can be fully automated.
•	Not a demo that stops working the moment the hackathon ends.
3.3 Core principles
Principle	Meaning
Coexist, don’t replace	Preserve existing systems of record; integrate via adapters.
Decision intelligence over prediction	A prediction only matters if it changes a decision.
Plan for reality, not perfection	Model overruns, delay, uncertainty, changing state.
Safety before optimization	Hard constraints are never traded for efficiency.
Human-authorized execution	AI recommends; an authorized person approves or modifies.
Explain every material recommendation	Every plan answers “why this, and why not the alternative.”
Simulate before commitment	Evaluate consequences before a plan is accepted.
Modular, model-agnostic	ML/optimization implementations can change without a redesign.
Outcome feedback	Capture decisions and actual outcomes to improve future recommendations.
4. Problem Definition
Dimension	Failure mode today	Required intelligence
Maintenance demand	Important work is overdue, scattered, or poorly prioritized	Risk and priority scoring
Block availability	A suitable window conflicts with trains or other work	Constraint-aware block planning
Cross-department work	Engineering, S&T, TRD request separate access windows	Task bundling and coordination
Train operations	Blocks create direct or downstream delay	Train–block coordination
Uncertain duration	Work takes longer than planned	Robust scheduling and contingency analysis
Asset failure	Infrastructure suddenly becomes unavailable	Disruption assessment and recovery planning
Plan degradation	Actual state diverges from approved plan	Continuous state reconciliation and re-planning
Decision transparency	Users can’t see why a schedule was chosen	Explainable recommendations and audit trail
5. Stakeholders & Users
Role	Need	RAILMIND value
Operations management	Network visibility, trade-offs	Command center, scenario comparison
Traffic/operations controller	Efficient, safe train movement	Live impact view, conflict + recovery options
Engineering planner	Complete work efficiently	Prioritization, block opportunities, bundling
S&T / TRD planner	Coordinate signalling/traction work	Shared possession planning, cross-department coordination
Maintenance supervisor	Execute work in realistic windows	Task readiness, duration uncertainty visibility
Asset manager	Maintain availability, reduce risk	Asset health, criticality, maintenance intelligence
Senior decision-maker	Choose operational trade-offs	Alternatives, impact summaries, explanations
6. Scope Tiers (resolves the “over-engineering vs. industry-grade” tension)
The prior documents were criticized for being enterprise-scale vision without a buildable core. The fix is not to shrink the ambition — it’s to tier it explicitly, so the industry-grade architecture remains true and the SIH commitment stays honest.
Tier	Scope	Status for SIH
Tier 1 — SIH Build	Single bounded corridor, full closed-loop demo (plan → optimize → simulate → disrupt → recover), real CP-SAT solver, real ML models on synthetic data, modular monolith, one deployment target	Must be built and working before the deadline. This is the only tier the team is accountable for delivering in code.
Tier 2 — Pilot-Ready	Real historical data ingestion, event-driven integration adapters, multi-division scope, role-based governance, monitoring	Documented as immediate next phase; not built for SIH, but interfaces in Tier 1 are designed so Tier 2 doesn’t require a rewrite.
Tier 3 — Platform Vision	Multi-zone deployment, resource/energy/freight optimization, weather intelligence, continuous learning loop, enterprise security	Roadmap and pitch material only. Explicitly labelled as vision in the PPT — never implied as delivered.
This tiering is the single most important fix from v0.1: it lets the team keep the strong architecture as their differentiator in the pitch, without the judges (or the team) confusing vision slides for working software.
7. SIH26027 Tier-1 MVP — Exact Scope
23.	Represent a bounded railway corridor with track sections, stations, assets and dependencies (see §12 for exact sizing).
24.	Represent maintenance tasks with priority, duration, resource and location attributes.
25.	Represent a train schedule and operational constraints for the same corridor and horizon.
26.	Prioritize maintenance work using an explainable scoring/ML approach.
27.	Generate candidate maintenance blocks via the CP-SAT formulation in §17.
28.	Bundle compatible multi-department tasks into shared possessions.
29.	Coordinate train movements around the proposed block (delay/holding/re-sequencing).
30.	Optimize the combined plan against hard constraints and weighted objectives.
31.	Simulate operational impact of the proposed plan (baseline + Monte Carlo overrun scenarios).
32.	Demonstrate an overrun/what-if scenario end-to-end.
33.	Demonstrate sudden track unavailability end-to-end.
34.	Generate a recovery/re-planning recommendation.
35.	Show explanation, ranked alternatives and a human approval step in the UI.
7.1 MVP non-goals (explicit, so nobody accidentally scope-creeps)
•	National-scale or multi-division optimization.
•	Direct/autonomous control of trains or safety-critical equipment.
•	Full replication of TMS/SMMS/TDMS/BDMS as systems of record.
•	Real integration with production railway systems (no access exists for this cycle).
•	A microservices deployment (a modular monolith is the correct choice at this scale — see §22).
•	Deep learning used for novelty rather than necessity (GNNs, transformers, etc. are Tier 2/3 unless the team has verified bandwidth — see §16.4).
8. Reference Demonstration Script (what actually gets shown to judges)
1.	Load the bounded corridor: assets, maintenance backlog, train schedule (§12 dataset).
2.	AI ranks the maintenance backlog by explainable priority score.
3.	System identifies compatible cross-department tasks and proposes a bundle.
4.	Optimizer proposes a block window; train impact is computed and shown.
5.	Simulation shows baseline delay/risk for the proposed plan versus 1–2 alternatives.
6.	A human approves the plan (role-gated UI action, logged to the audit trail).
7.	Live: the active block overruns by a configured amount → system detects the deviation.
8.	Affected trains are recalculated; a revised plan is recommended with a stated rationale.
9.	Live: a second, independent disruption is triggered — a track section becomes unavailable.
10.	System invalidates dependent plans, generates ranked recovery alternatives, simulates each, and presents them with explanation.
11.	Human compares and approves a recovery plan; the decision and outcome are recorded.
This is the entire pitch. Every module built for Tier 1 exists to make this script real, not scripted/faked.
________________________________________
PART B — CANONICAL DATA MODEL & DEMO DATASET
9. Why this section exists
Both source documents referred repeatedly to “synthetic data” and “a bounded corridor” without ever defining either. That ambiguity is the single biggest execution risk identified in review — no team member can build against an undefined shape. This section fixes it with an explicit schema and explicit sizing [ASSUMPTION].
10. Core Domain Entities
RailwayNetwork
 ├── Zone
 ├── Division
 ├── Section        (edge in the network graph; has capacity, length, speed)
 ├── Station         (node in the network graph)
 ├── Track
 └── Infrastructure  (signals, OHE, bridges, points)

Asset
 ├── TrackAsset
 ├── SignalAsset
 ├── OHEAsset
 ├── Bridge
 └── ElectricalAsset

MaintenanceTask
 ├── Defect
 ├── PreventiveMaintenance
 ├── CorrectiveMaintenance
 └── Inspection

Block (Possession)
 ├── RequestedBlock
 ├── ApprovedBlock
 ├── ActiveBlock
 └── CompletedBlock

Train
 ├── PassengerTrain
 ├── GoodsTrain
 └── SpecialTrain

Resource
 ├── Crew (department-qualified)
 ├── Equipment
 └── Machinery

Incident
 ├── AssetFailure
 ├── TrackDamage
 └── ExternalDisruption

Plan / Scenario / Recommendation / Decision / Outcome
11. Canonical Schema (field-level)
11.1 Section
Field	Type	Notes
section_id	string (PK)	e.g. SEC-04
from_station_id	string (FK)	
to_station_id	string (FK)	
length_km	float	
track_count	int	single/double/multi
max_speed_kmph	int	
department_owners	list[enum]	Engineering, S&T, TRD, OHE
criticality	enum	LOW / MEDIUM / HIGH / CRITICAL
11.2 MaintenanceTask
Field	Type	Notes
task_id	string (PK)	
section_id	string (FK)	
department	enum	Engineering, S&T, TRD, OHE
task_type	enum	Preventive, Corrective, Inspection, Defect
expected_duration_min	int	point estimate
duration_p10_min / duration_p90_min	int	uncertainty band, feeds §17.2
crew_size_required	int	
crew_qualification	enum	matches Crew.department
criticality	enum	LOW / MEDIUM / HIGH / CRITICAL
overdue_days	int	0 if not overdue
dependency_task_ids	list[string]	precedence, may be empty
earliest_start	datetime	
latest_finish	datetime	deadline, may be null
11.3 CandidateBlockWindow
Field	Type	Notes
window_id	string (PK)	
section_id	string (FK)	
earliest_start	datetime	
latest_end	datetime	
max_duration_min	int	
11.4 TrainService
Field	Type	Notes
train_id	string (PK)	
train_type	enum	Passenger, Goods, Special
priority	int	1 (highest) – 5
route	list[section_id]	ordered
scheduled_departure / arrival per section	datetime	timetable
11.5 Resource (Crew Pool)
Field	Type	Notes
department	enum	Engineering, S&T, TRD, OHE
available_crew_count	int	per shift, per day
shift_window	tuple[datetime]	
11.6 Block (output of optimization)
Field	Type	Notes
block_id	string (PK)	
section_id	string (FK)	
start_time / end_time	datetime	
assigned_task_ids	list[string]	
status	enum	Requested, Approved, Active, Completed, Overrun
plan_version	int	see §21
12. Demo Dataset Sizing [ASSUMPTION — revise once real corridor is confirmed]
To make “bounded corridor” concrete:
Parameter	Value
Corridor	1 division, single line, 6 stations, 9 track sections
Planning horizon	3 days (72 hours)
Train services	48 (34 passenger, 14 goods), realistic headways
Maintenance tasks	22, across all 4 departments, 3 marked overdue, 4 marked CRITICAL
Candidate block windows	4–6 per section per day (night-heavy, consistent with typical possession patterns)
Crew pools	4 departments × 2 shifts × 3–6 crew per shift
Disruption events for demo	1 scripted block overrun (+45 min), 1 scripted TRACK_UNAVAILABLE incident
This sizing is deliberately small enough to solve in seconds with CP-SAT, and large enough to produce genuine conflicts (i.e., a naive greedy scheduler visibly performs worse than the optimizer — this contrast is itself a demo point).
________________________________________
PART C — SYSTEM ARCHITECTURE
13. Architectural Principles
13.1 Existing-system coexistence
RAILMIND integrates with existing systems (TMS, SMMS, TDMS, BDMS, COA, GIS, asset registers) via adapters. It does not become a new system of record for anything those systems already own.
13.2 Responsibility split — “ML predicts, rules constrain, optimization decides, simulation evaluates, humans decide”
Engine	Answers	Boundary
ML / statistical models	What is likely to happen? (duration, delay, failure risk, priority)	Predictive estimate only — never final authority
Rules / policy engine	What must never be violated?	Deterministic; hard constraints cannot be optimized away
Optimization engine	What is the best feasible plan?	Must satisfy every hard constraint from the rules engine
Simulation engine	What happens if we execute this, or if assumptions change?	Scenario evaluation; never direct execution
LLM / copilot (optional)	How can the system explain or answer a natural-language query?	Assistive only; may not invent facts or override structured outputs
Human	What should actually happen?	Sole authority for approval and execution
14. High-Level Architecture
EXISTING RAILWAY SYSTEMS (TMS / SMMS / TDMS / BDMS / COA / Timetable / GIS / Assets)
        │
        ▼
INTEGRATION FABRIC (API Gateway, System Adapters, Event Gateway, Batch/File Ingestion, Validation)
        │
        ▼
RAILWAY DATA PLATFORM (Canonical Model, Operational Store, Historical Lake, GIS/Network Model, Event Store)
        │
        ▼
RAILWAY STATE ENGINE (PLAN / ACTUAL / PREDICTION / SCENARIO, Dependency Graph, State Versioning)
        │
   ┌────┴─────┐
   ▼          ▼
INTELLIGENCE   DOMAIN RULES ENGINE
LAYER (ML)     (Hard/Soft Constraints, Policy Versioning)
   └────┬─────┘
        ▼
OPTIMIZATION PLATFORM (Block Optimization, Task Bundling, Train Coordination, Recovery Optimization)
        │
        ▼
DIGITAL TWIN / SIMULATION (Scenario Engine, Delay Propagation, Monte Carlo)
        │
        ▼
DECISION INTELLIGENCE LAYER (Candidate Plans, Risk, Explanation, Alternatives)
        │
        ▼
HUMAN-IN-THE-LOOP (Approve / Modify / Reject / Compare)
        │
        ▼
CONTROLLED EXECUTION (Existing Authorized Railway Workflows)
        │
        ▼
ACTUAL OUTCOME ──────────────► FEEDBACK LOOP → STATE ENGINE
15. Architectural Layers & Module Responsibilities (unified — no duplication with product modules)
Layer	Responsibility	Tier-1 implementation
L0 — Existing Railway Systems	Systems of record for maintenance, block, ops, infra	Simulated via synthetic dataset (§12)
L1 — Integration Fabric	Ingestion, adapters, validation, provenance	Batch/file ingestion of synthetic CSV/JSON only
L2 — Railway Data Platform	Canonical model, operational store, historical data	PostgreSQL + PostGIS
L3 — Railway State Engine	Current/planned/predicted/scenario state, versioning	Backend domain service, state versioned per change
L4 — Intelligence Layer (ML)	Duration, delay, priority, failure-risk prediction	scikit-learn / XGBoost (see §16)
L5 — Domain Rules Engine	Hard/soft constraints, policy versioning	Python rules module, versioned constraint sets
L6 — Optimization Platform	Block optimization, bundling, train coordination	OR-Tools CP-SAT (see §17)
L7 — Digital Twin / Simulation	What-if, Monte Carlo, delay propagation	Python discrete-event simulation
L8 — Disruption Intelligence	Incident classification, impact analysis, recovery generation	Rules + re-invocation of L6/L7 on updated state
L9 — Decision Intelligence	Ranks options, packages explainable recommendations	Backend orchestration + template-based explanation
L10 — Human Experience	Role-based dashboards, planning, simulation, approval	React / Next.js
L11 — Governance	Identity, RBAC, audit, versioning	Tier 1: basic RBAC + append-only audit log; full governance is Tier 2
16. Intelligence Layer — Concrete Model Specifications
16.1 Maintenance Duration Prediction
•	Input features: task_type, department, asset_type, section criticality, crew size, historical duration for this task/asset type, time-of-day, day count since last similar task.
•	Model: Gradient-boosted trees (XGBoost) regression, trained on synthetic historical duration records with injected noise to create realistic variance.
•	Output: expected duration, P10/P90 interval, overrun risk (probability duration exceeds latest_finish constraint).
•	Why not a GNN here: duration prediction is a tabular regression problem; a GNN adds complexity without benefit for this specific model. GNNs are reserved for §16.4.
16.2 Maintenance Priority Score
Weighted, explainable scoring function (not a black box) — deliberately chosen over an opaque model because judges and operators need to see why a task ranked where it did:
priority_score(task) =
      w1 * criticality_score(task.criticality)
    + w2 * normalize(task.overdue_days)
    + w3 * failure_risk(task.asset_id)      # from asset risk model
    + w4 * safety_flag(task.task_type)
    + w5 * downstream_impact(task.section_id)  # trains/day on this section
Default weights [ASSUMPTION]: w1=0.30, w2=0.20, w3=0.20, w4=0.20, w5=0.10 — exposed as configuration, not hard-coded, so they can be tuned live in a demo.
16.3 Train Delay / Impact Prediction
•	Input: proposed block window, section, affected train IDs, train priority, historical delay patterns for the section, time of day.
•	Model: Gradient-boosted regression for direct delay per train; a simple graph-propagation pass (using the section-adjacency graph, NetworkX) for downstream/cascading delay on connected sections.
•	Output: expected delay per affected train, confidence.
16.4 GNN-based cascading delay prediction — status
The team’s public materials reference a GNN for cascading delay prediction. Recommendation: build the NetworkX-based graph-propagation baseline first (§16.3) since it is explainable and always finishes on time; attempt a GNN (e.g., a small GraphSAGE model over the section-adjacency graph) only as a stretch enhancement once the baseline demo is fully working end-to-end. Do not let the GNN block the core deliverable — this is the top technical risk if left unscoped.
16.5 Anomaly Detection (Tier 2)
Statistical control-chart or isolation-forest detection over duration/delay residuals — flagged as Tier 2, not required for the Tier-1 demo script.
17. Optimization — Concrete CP-SAT Formulation
This directly replaces the placeholder text from v0.1 (“the exact mathematical formulation should be established”).
17.1 Sets and indices
•	T — maintenance tasks, indexed t
•	W — candidate block windows, indexed w (each w belongs to exactly one section sec(w))
•	R — trains, indexed r; each train has an ordered route of sections
•	D — departments (crew pools), indexed d
17.2 Parameters
•	dur_t — expected duration of task t (minutes); dur_t_p90 — 90th-percentile duration for robustness checks
•	crew_t — crew size required by task t; dept(t) — department of task t
•	priority_t — priority score from §16.2
•	avail_d,shift — available crew count for department d in a given shift
•	[e_w, l_w] — earliest start / latest end of window w; maxdur_w — max usable duration of window w
•	delay_pred(w, r) — predicted delay to train r if window w is activated (from §16.3), or 0 if r does not use sec(w) during [e_w, l_w]
•	dep(t, t') — 1 if task t must precede task t'
17.3 Decision variables
•	x[t,w] ∈ {0,1} — task t assigned to window w
•	y[w] ∈ {0,1} — window w is activated (becomes an actual block)
•	start[w], end[w] ∈ ℤ — actual start/end time of block w (as CP-SAT IntervalVar, active only if y[w]=1)
•	delay[r] ∈ ℤ⁺ — total predicted delay for train r
•	unscheduled[t] ∈ {0,1} — 1 if task t is not scheduled this horizon (slack variable, penalized in the objective rather than forbidden, so the model always stays feasible)
17.4 Hard constraints
1.	Assignment: Σ_w x[t,w] + unscheduled[t] = 1 for every task t.
2.	Window activation: x[t,w] ≤ y[w] for every t, w.
3.	Crew qualification: x[t,w] = 0 if dept(t) has no qualified crew available in the shift covering window w.
4.	Crew capacity (cumulative constraint): for each department d and shift, Σ_t crew_t · x[t,w] (summed over concurrent windows) ≤ avail_d,shift — implemented with CP-SAT’s AddCumulative.
5.	Section exclusivity (no-overlap): for all windows w, w' on the same section, their IntervalVars must not overlap — implemented with CP-SAT’s AddNoOverlap per section.
6.	Duration feasibility: end[w] - start[w] ≥ Σ_t dur_t · x[t,w] (sequential execution within a possession; parallel-crew bundling is a Tier 2 refinement using per-crew sub-intervals).
7.	Window bounds: e_w ≤ start[w], end[w] ≤ l_w, end[w] - start[w] ≤ maxdur_w.
8.	Task precedence: if dep(t,t')=1 and both are scheduled, the window containing t' must start no earlier than the window containing t ends.
9.	Deadline: if task t has a latest_finish, any window assigned to it must satisfy end[w] ≤ latest_finish.
17.5 Objective function
Minimize:
      α · Σ_r delay[r]                              # train disruption
    + β · Σ_t unscheduled[t] · priority_t            # unmet high-priority maintenance
    + γ · Σ_w y[w]                                   # block fragmentation (fewer, better-bundled blocks)
    + δ · Σ_w y[w] · overrun_risk(w)                  # prefer robust windows (from §16.1 P90 data)
    − ε · Σ_t,w x[t,w] · bundle_bonus(t,w)            # reward cross-department bundling in the same window
Default weights [ASSUMPTION, expose as config]: α=5, β=4, γ=1, δ=2, ε=1 — tuned so train delay dominates but does not make maintenance backlog invisible; expose as sliders in the planning UI so judges can see the trade-off live.
delay[r] is computed post-hoc from delay_pred(w, r) for every activated window w whose active train conflicts are unresolved (i.e., not fully absorbed by re-sequencing) — this is the coupling point between the block optimizer and train coordination, kept as one joint model rather than two sequential ones, per the product principle in §3.1.
17.6 Robustness pass (Tier 1, simplified Monte Carlo)
After the CP-SAT solve produces a candidate plan, run N=200 Monte Carlo draws sampling each dur_t from its [P10, P90] band; re-check constraint 6 and 7 under each draw; report P(overrun) per block and P(any-plan-violation) overall. This is what powers the “Plan B has lower overrun risk” comparison in the decision UI (§19) and is a direct, buildable stand-in for the “robust optimization” language in v0.1 that was previously only described conceptually.
18. Simulation & Digital Twin (Tier 1 scope)
The digital twin is computational, not 3D. For Tier 1 it maintains: network state (sections/stations), train positions/delays, active block state, and resource allocation — all backed by the same canonical model as the optimizer, so simulation results and optimizer inputs never disagree.
Scenario engine: every what-if scenario is a copy-on-write branch of the live state (Scenario A/B/C); no scenario can mutate the live operational state. Each scenario returns: total delay, affected trains, affected blocks, maintenance completion, and the Monte Carlo risk profile from §17.6.
19. Disruption & Recovery Intelligence
19.1 Block overrun flow
Block Active → Actual Duration Increasing → BLOCK_OVERRUN event
  → State Update → Identify Affected Trains → Predict Delay Propagation
  → Re-invoke §17 optimizer on the updated state (only the affected window + downstream windows are re-solved, not the whole horizon)
  → Simulate candidates → Rank by objective (§17.5) → Recommend → Human Approval
19.2 Sudden infrastructure loss flow
TRACK_UNAVAILABLE event → Incident classification → Affected section(s) via dependency graph
  → Invalidate plans depending on the section → Identify affected trains/blocks/tasks
  → Generate recovery candidates (reschedule block, reroute/hold trains, reassign crew)
  → Re-solve §17 model with the section removed from the window set
  → Simulate each candidate → Rank → Present to authorized operator
Both flows reuse the same CP-SAT model with an updated state — this is why the PLAN/ACTUAL/PREDICTION/SCENARIO separation (§20) matters: recovery is not a separate algorithm, it’s the same optimizer solving a smaller, updated problem.
20. State Model — PLAN / ACTUAL / PREDICTION / SCENARIO
This is retained unchanged from the architecture v1.0 draft because it was correctly identified as one of the strongest design decisions in the original material.
PLAN      → what was intended (the approved output of §17)
ACTUAL    → what is happening (fed by events, e.g. BLOCK_OVERRUN)
PREDICTION → what the system expects to happen next (ML output)
SCENARIO  → what could happen (simulation branch, never mutates live state)
Every state change creates a new version (state v1021 → v1022 → ...); every optimization/recommendation references the exact state version it was computed against — this is what makes a recommendation reproducible and auditable (§24).
21. Explainability
Every recommendation is generated from structured decision evidence, not free text:
Recommendation
 ├── recommendation_id, state_version, plan_version, model_version
 ├── recommended_action, expected_outcome (delay, risk, robustness)
 ├── affected_trains / affected_maintenance / affected_resources
 ├── constraint_trace          # which hard constraints bound the solution
 ├── objective_breakdown       # contribution of each term in §17.5
 ├── alternatives              # top-3 ranked alternatives with their deltas
 └── evidence                  # ML predictions and their confidence used as inputs
Example rendering to a human user:
Task T-102 is CRITICAL and 5 days overdue. Block B bundles it with 2 compatible S&T tasks. Expected passenger impact: 11 minutes across 2 trains. Alternative Block C would cause 37 minutes of predicted disruption and has a higher overrun risk (24% vs. 9%). Recommended: Block B.
An optional LLM layer may turn objective_breakdown + constraint_trace into this kind of natural-language sentence, but it consumes structured evidence — it never generates the numbers itself.
22. Engineering Architecture (Tier 1 build discipline)
•	Modular monolith, not microservices, for the SIH build — logical module boundaries (State, Integration, Maintenance, Block Planning, Train Intelligence, Optimization, Simulation, ML Inference, Decision, Event, Audit) exist as Python packages within one FastAPI service, with async workers for optimization/simulation jobs.
•	Prediction, optimization, simulation and explanation sit behind explicit interfaces (Python protocols/ABCs) so a model or solver can be swapped without touching the orchestration layer.
•	Every optimization run records: state version, constraint set version, objective weights, solver version, and result — enabling reproducibility (§24) with a handful of extra columns, not a new subsystem.
•	Rules for hard safety/operational constraints are deterministic and versioned separately from ML models.
•	Offline/simulation mode (no live integration required) is the default mode for Tier 1, not a fallback bolted on later.
23. API Surface (Tier 1)
/api/v1/network
/api/v1/assets
/api/v1/maintenance
/api/v1/blocks
/api/v1/trains
/api/v1/resources
/api/v1/events
/api/v1/plans
/api/v1/scenarios
/api/v1/disruptions
/api/v1/recommendations
/api/v1/decisions
24. Governance & Audit (Tier 1 minimum, Tier 2 full)
Tier 1 (build this): - Role-based access with 3 roles minimum: Planner, Controller, Approver. - Append-only audit table: user, action, timestamp, state_version, previous_value, new_value. - Every optimization/recommendation is reproducible from (state_version, constraint_version, objective_weights, solver_version) — no extra infrastructure required beyond disciplined column design.
Tier 2/3 (roadmap only): SSO/enterprise identity, division/zone-scoped permissions, ML governance dashboards (drift monitoring), immutable/cryptographically-protected audit storage, full observability stack (OpenTelemetry, Prometheus, Grafana).
25. Technology Stack
Area	Tier 1 (build this)	Tier 2/3 (roadmap)
Frontend	React + Next.js + TypeScript	MapLibre/Deck.gl network visualization at scale
Backend	Python, FastAPI, Pydantic, SQLAlchemy	Service extraction where scale demands
Database	PostgreSQL + PostGIS	Read replicas, sharding
Optimization	Google OR-Tools CP-SAT	MILP solver comparison, custom heuristics for very large instances
ML	scikit-learn, XGBoost	GNN (§16.4, stretch), PyTorch if justified
Graph	NetworkX	Graph database if scale requires
Simulation	Python discrete-event + Monte Carlo	Higher-fidelity network simulation
Messaging	In-process + Redis (optional)	Kafka/Redpanda at production event volume
Deployment	Docker Compose	Kubernetes
Observability	Structured logging + basic metrics	OpenTelemetry, Prometheus, Grafana
26. Non-Functional Requirements (Tier 1 targets)
•	CP-SAT solve time on the §12 dataset: target under 10 seconds for a full-horizon solve, under 2 seconds for a re-plan after a disruption event (only affected windows re-solved).
•	UI interactions (browsing plans, viewing recommendations): sub-second for a corridor of this size.
•	All demo scenarios must be deterministic and re-runnable (same seed → same outcome) for reliable live demos.
________________________________________
PART D — DELIVERY
27. Immediate Team Execution Plan (sequenced, not parallel-everything)
1.	Lock the canonical schema (§11) and generate the demo dataset (§12) — this unblocks every other workstream.
2.	Build the CP-SAT model (§17) against the dataset as a standalone script, validated against hand-checkable small cases before wiring it to a UI.
3.	Build the priority scoring (§16.2) and duration/delay prediction baselines (§16.1, §16.3) — tabular models only; defer §16.4 (GNN).
4.	Wire optimizer output into the state model (§20) with versioning from day one — retrofitting this later is expensive.
5.	Build the minimum backend API surface (§23) needed for the demo script (§8), not the full API list.
6.	Build the frontend planning + simulation + disruption workspace against the real API — no mocked data once the backend is running.
7.	Script and rehearse the exact demo (§8) end-to-end, including the two disruption triggers, before polishing UI visuals.
8.	Only after the full script works: attempt the GNN stretch goal (§16.4), Monte Carlo UI polish, and any Tier 2 teasers for the pitch deck.
28. Success Metrics & Impact Framework
Metric family	Example KPI
Asset availability	Increase in available/usable asset time vs. naive greedy baseline
Maintenance efficiency	Tasks completed per block; overdue-work reduction; block utilization
Train operations	Total delay minutes; affected trains; delay propagation
Planning quality	Constraint violations (should be zero); feasibility rate; re-planning success rate
Robustness	P(overrun) from §17.6; performance under the two scripted disruptions
Recovery	Time to generate a recovery plan; recovery delay vs. baseline
Decision quality	Predicted vs. actual outcome for scripted scenarios
The prototype should demonstrate comparative improvement against a naive greedy/manual baseline, computed on the same dataset — not an invented absolute claim. Build the naive baseline (simple earliest-fit, no optimization) early; it is cheap and gives every later result a number to compare against, which is what judges will ask for.
29. Risks & Mitigations
Risk	Mitigation
Over-scoping	Tiering in §6; Tier 1 is the only committed deliverable
Limited/no real data	Rigorously structured synthetic dataset (§12) with documented assumptions
Optimization complexity	Bounded corridor size (§12), formulation validated on hand-checkable small cases first
GNN/advanced-ML overreach	Explicitly deferred to stretch goal (§16.4); tabular baselines are the committed deliverable
Black-box perception	Explainability evidence structure (§21); weighted, inspectable priority score (§16.2)
Unsafe-automation perception	Human-in-the-loop approval gate is present in every flow, demoed explicitly
Demo failure live	All scenarios deterministic and seeded (§26); rehearsed script (§8)
Documentation-over-code drift	This single document replaces both prior documents; no parallel vision doc to maintain
30. Roadmap
Phase	Scope
Phase 0 — SIH Tier 1	Bounded corridor, full closed loop, CP-SAT, tabular ML, deterministic demo
Phase 1 — Pilot (Tier 2)	Real historical data, event-driven integration, role/permission depth, monitoring
Phase 2 — Adaptive Platform (Tier 2/3)	Delay propagation at scale, GNN cascading-delay model, continuous re-planning
Phase 3 — Multi-Division (Tier 3)	Multiple corridors/divisions, richer digital twin, resource optimization
Phase 4 — Railway Intelligence Platform (Tier 3)	Weather/energy/freight intelligence, continuous learning loop, enterprise governance
31. Differentiation
•	Railway-specific decision model, not a generic scheduler.
•	Joint maintenance + train coordination in a single optimization model (§17.5), not two disconnected passes.
•	Robust planning via explicit uncertainty bands and Monte Carlo risk (§17.6), not point-estimate scheduling.
•	Disruption recovery reuses the same optimizer on updated state (§19), not a separate bespoke algorithm.
•	Explainable by construction (§21) — every number in a recommendation traces to a structured input.
•	Tiered, honest scope (§6) — the pitch can show the full platform vision without misrepresenting what runs live.
________________________________________
Appendix — Working Glossary
Term	Definition
Block / Possession	A controlled period during which specified infrastructure is unavailable for authorized work
Railway state	Current + planned representation of infrastructure, assets, trains, maintenance, blocks, resources, events
Digital twin	Computational representation of the network and its state, used for simulation and optimization
Robust schedule	A schedule that stays acceptable under plausible duration/delay deviations, not just the point-estimate optimum
What-if scenario	A copy-on-write branch of state used to evaluate an alternative assumption without touching live state
Recovery plan	A feasible plan generated after disruption invalidates the original plan, via re-solving §17 on updated state
Canonical model	Normalized representation of railway entities, independent of any one source system’s schema
CP-SAT	Google OR-Tools’ constraint-programming SAT solver, used for the block/task scheduling model in §17
________________________________________
Versioning note: v1.0 is build-ready for the SIH26027 Tier-1 scope. All [ASSUMPTION]-tagged values (dataset sizing, objective weights, priority-score weights) are configuration, not hard-coded constants, and should be the first things tuned once the team has a working end-to-end pipeline.
