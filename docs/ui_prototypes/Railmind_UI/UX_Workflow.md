RAILMIND
Railway Maintenance, Operations & Block Intelligence Platform
UI/UX & Operational Workflow Specification
Document Version: 1.0
Status: Product Design Baseline
Design Classification: Professional / Enterprise Operational Software
Primary Users: Railway planners, controllers, maintenance planners, supervisors, approvers, operations management
Design Philosophy: Decision Workspace, not Dashboard
Core Principle: Human-authorized decision intelligence
________________________________________
1. Executive Design Statement
RAILMIND should not look like:
•	a college dashboard
•	an AI chatbot
•	a generic analytics platform
•	a collection of KPI cards
•	a railway-themed admin panel
•	a “smart AI” demo
RAILMIND should feel like a professional operational command system.
The user should be able to open RAILMIND and immediately answer:
What is happening?
Then:
What needs my attention?
Then:
What can I do?
Then:
What happens if I do it?
Then:
Why is RAILMIND recommending this?
Then:
What changes if I choose another option?
And finally:
Am I authorized and confident enough to approve it?
This produces the fundamental UX loop:
OBSERVE
   ↓
UNDERSTAND
   ↓
INVESTIGATE
   ↓
GENERATE OPTIONS
   ↓
SIMULATE
   ↓
COMPARE
   ↓
DECIDE
   ↓
APPROVE
   ↓
MONITOR
   ↓
RECOVER
________________________________________
2. Product UX Philosophy
RAILMIND’s interface is built around decision-making under operational pressure.
The product should optimize for:
1.	situational awareness
2.	prioritization
3.	low cognitive load
4.	rapid investigation
5.	consequence visibility
6.	explainability
7.	confidence
8.	controlled action
9.	traceability
10.	recovery
The UI should never make the operator hunt through ten screens to understand the consequence of a decision.
________________________________________
3. The RAILMIND UX Mental Model
The product should be understood as five layers.
┌──────────────────────────────────────┐
│ 1. SITUATION                         │
│ What is happening now?               │
├──────────────────────────────────────┤
│ 2. INTELLIGENCE                      │
│ What does the system know/predict?   │
├──────────────────────────────────────┤
│ 3. OPTIONS                           │
│ What can we do?                      │
├──────────────────────────────────────┤
│ 4. CONSEQUENCES                      │
│ What happens for each option?        │
├──────────────────────────────────────┤
│ 5. DECISION                          │
│ What should the authorized user do? │
└──────────────────────────────────────┘
This is the core UX architecture.
________________________________________
4. Product Navigation Architecture
RAILMIND should use a persistent operational shell.
┌───────────────────────────────────────────────────────────────┐
│ RAILMIND    Corridor ▼   06 Sep 2026 21:42    Alerts  User    │
├──────────────┬────────────────────────────────────────────────┤
│              │                                                │
│ Command      │                                                │
│ Center       │                                                │
│              │                                                │
│ Operations   │                                                │
│              │                                                │
│ Maintenance  │              WORKSPACE                         │
│              │                                                │
│ Block        │                                                │
│ Planning     │                                                │
│              │                                                │
│ Trains       │                                                │
│              │                                                │
│ Simulation   │                                                │
│              │                                                │
│ Disruptions  │                                                │
│              │                                                │
│ Decisions    │                                                │
│              │                                                │
│ Audit        │                                                │
│              │                                                │
│ Settings     │                                                │
└──────────────┴────────────────────────────────────────────────┘
The sidebar should remain stable.
The workspace changes.
This prevents users from feeling as though they are entering a completely different application every time they change modules.
________________________________________
5. Global Navigation
Primary navigation
Command Center
Global operational overview.
Operations
Train and infrastructure operational state.
Maintenance
Maintenance demand, risk and work.
Block Planning
Maintenance possession/block planning.
Simulation
Scenario and what-if analysis.
Disruptions
Active incidents and recovery.
Decisions
Recommendations, approvals and decisions.
Audit
Decision history and traceability.
________________________________________
6. Global Context Bar
Every workspace should know the current:
Division
Corridor
Planning horizon
State version
Scenario
Operational mode
Example:
Central Railway
› Division A
› Corridor C-07
› Next 72 Hours

LIVE
State v1021
If the user enters a scenario:
Central Railway
› Corridor C-07
› Scenario B

SIMULATION
Based on State v1021
The UI must make this distinction visually obvious.
________________________________________
7. PLAN / ACTUAL / PREDICTION / SCENARIO UX
This is one of RAILMIND’s strongest architectural concepts and should become a major UX principle.
The user should always know whether information represents:
PLAN
What should happen.
ACTUAL
What is happening.
PREDICTION
What RAILMIND expects.
SCENARIO
What could happen.
These must never visually look identical.
________________________________________
8. State Indicator
Every major operational object should display its state context.
Example:
BLOCK B-102

PLAN
01:00 — 02:30

ACTUAL
01:00 — 02:58

PREDICTION
Likely completion: 03:04

STATUS
OVERRUN
This prevents one of the most dangerous UX problems in operational software:
confusing what was planned with what is actually happening.
The underlying architecture explicitly requires these four state categories and versioned state changes.
________________________________________
9. Command Center
The Command Center is the home of RAILMIND.
It should not be a wall of charts.
Its purpose is:
Tell the operator what deserves attention right now.
________________________________________
10. Command Center Layout
┌──────────────────────────────────────────────────────────────┐
│ COMMAND CENTER                                               │
│ Corridor C-07 · Next 72 Hours · LIVE                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  OPERATIONAL STATE                                           │
│                                                              │
│  48 Trains       3 Active Blocks      4 Critical Tasks      │
│  2 Delays        1 Disruption         97% Network Available │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ⚠ REQUIRES ATTENTION                                       │
│                                                              │
│  BLOCK B-102   Overrun +28 min                 [Investigate] │
│  TRACK S4      Unavailable                     [Recover]    │
│  TASK T-221    Critical · 5 days overdue        [Review]    │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  NETWORK                                                       │
│                                                              │
│  Station ───── Section ───── Station ───── Section           │
│                ● BLOCK               ● DELAY                 │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  AI DECISIONS                                                │
│                                                              │
│  Recovery recommendation available              [Review]    │
│  3 high-impact maintenance tasks                [Plan]      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
________________________________________
11. Command Center Information Hierarchy
Priority order:
Level 1 — Exceptions
Something is wrong.
Level 2 — Decisions
Something requires a decision.
Level 3 — Risk
Something may become wrong.
Level 4 — Operations
What is currently happening.
Level 5 — Analytics
Why it is happening.
The interface should therefore not give equal visual weight to every metric.
________________________________________
12. Alert Philosophy
Avoid:
47 notifications
Instead:
3 ACTIONABLE EVENTS
7 WATCH ITEMS
18 INFORMATIONAL
Alerts must be grouped by operational importance.
________________________________________
13. Alert Severity
Use semantic severity:
CRITICAL
HIGH
MEDIUM
LOW
INFO
But do not rely solely on color.
Every severity should also have:
•	icon
•	label
•	text
•	operational implication
This supports accessibility and reduces visual ambiguity.
________________________________________
14. Command Center “Attention Queue”
RAILMIND should maintain an intelligent attention queue.
Example:
┌───────────────────────────────────────────┐
│ ATTENTION QUEUE                           │
├───────────────────────────────────────────┤
│ 01  TRACK S4 UNAVAILABLE                  │
│     4 trains · 2 blocks affected          │
│     Recovery recommended                  │
│                                           │
│ 02  BLOCK B102 OVERRUN                    │
│     +28 min · 2 downstream trains        │
│     Recovery required                     │
│                                           │
│ 03  TASK T221 CRITICAL                    │
│     5 days overdue                        │
│     Next viable window: 02:00             │
└───────────────────────────────────────────┘
This is much more useful than a conventional notification drawer.
________________________________________
15. Operational Corridor Visualization
The corridor is one of the most important visual components.
It should represent:
Station
   │
Section
   │
Station
   │
Section
with operational overlays.
Example:
STN-A ───── S1 ───── STN-B ───── S2 ───── STN-C
             │                     │
           BLOCK                  DELAY
           B-102                  +12m
________________________________________
16. Corridor Visualization Rules
The visualization should support layers:
Infrastructure
•	stations
•	sections
•	assets
Operations
•	trains
•	train positions
•	delays
Maintenance
•	tasks
•	blocks
•	possessions
Risk
•	high-risk assets
•	predicted overrun
Disruption
•	unavailable sections
•	affected routes
Scenario
•	hypothetical changes
Users should be able to toggle layers without changing the underlying workspace.
________________________________________
17. Maintenance Workspace
The Maintenance workspace answers:
What work needs to happen, how urgent is it, and when should we do it?
________________________________________
18. Maintenance Queue
Primary table:
Priority	Task	Asset	Department	Due	Risk	Duration	Recommended
Critical	T-102	A-44	Eng.	-5d	High	90m	B-102
Critical	T-117	A-21	S&T	-2d	High	60m	B-102
High	T-121	A-62	TRD	1d	Med	45m	B-104
The table should support:
•	filtering
•	sorting
•	grouping
•	saved views
•	column customization
•	bulk inspection
________________________________________
19. Maintenance Task Detail
Clicking a task opens a contextual detail panel rather than forcing the user away from the table.
TASK T-102
━━━━━━━━━━━━━━━━━━━━

CRITICAL
5 days overdue

Asset
A-44

Section
S4

Department
Engineering

Failure Risk
78%

Predicted Duration
90 min

P10
72 min

P90
118 min

Recommended Window
B-102 · 01:00–02:30

Why?
• Critical asset
• 5 days overdue
• High failure risk
• Compatible with 2 S&T tasks
________________________________________
20. Priority Explanation
The priority score must never be presented as:
AI Score: 0.91
without explanation.
Instead:
PRIORITY: CRITICAL

Contributing factors

Asset criticality       ██████████
Overdue duration        ████████
Failure risk            ███████
Safety relevance        ████████
Downstream impact       ████
This makes the intelligence actionable.
________________________________________
21. Block Planning Workspace
This is the heart of RAILMIND.
It should be a planning canvas, not a form.
________________________________________
22. Block Planning Canvas
Recommended layout:
┌───────────────────────────────────────────────────────────────┐
│ BLOCK PLANNING                              [Generate Plan]   │
├───────────────┬───────────────────────────────────────────────┤
│ TASK QUEUE    │                 TIMELINE                     │
│               │                                               │
│ T-102 ●       │ 00  01  02  03  04  05  06                  │
│ T-117 ●       │                                               │
│ T-121 ○       │ S1 ────────████ B102 ████────────             │
│ T-131 ○       │ S2 ───────────────████ B104 ████────          │
│               │                                               │
│               │ Train 201 ────────╲                          │
│               │ Train 304 ─────────╲── DELAY +11m            │
│               │                                               │
├───────────────┴───────────────────────────────────────────────┤
│ OPTIMIZATION SUMMARY                                          │
│ Delay ↓  | Blocks ↓ | Completion ↑ | Overrun Risk ↓          │
└───────────────────────────────────────────────────────────────┘
________________________________________
23. Timeline UX
The timeline should visually combine:
maintenance
+
blocks
+
trains
+
resource availability
This is important because RAILMIND’s value comes from joint planning rather than independent maintenance scheduling.
________________________________________
24. Task Bundling Interaction
Users should be able to visually see compatible work.
Example:
B-102
━━━━━━━━━━━━━━━━━━━━━━

Engineering
T-102 █████████

S&T
T-117 ██████

TRD
T-121 ████

Bundling Benefit
+3 tasks / same possession

Predicted impact
11 min
The user should understand why these tasks were grouped.
________________________________________
25. “Generate Plan” Interaction
The primary planning action should not immediately commit anything.
Click:
Generate Plan
produces:
Generating candidate plans...

✓ Maintenance prioritized
✓ Candidate windows generated
✓ Constraints evaluated
✓ CP-SAT optimization completed
✓ Train impact calculated
✓ Simulation completed
✓ Robustness evaluated
Then:
3 CANDIDATE PLANS READY
________________________________________
26. Plan Comparison
This should be one of the signature RAILMIND experiences.
┌─────────────────────────────────────────────────────────────┐
│ PLAN COMPARISON                                             │
├────────────┬─────────────┬─────────────┬───────────────────┤
│            │ PLAN A      │ PLAN B ★    │ PLAN C            │
├────────────┼─────────────┼─────────────┼───────────────────┤
│ Delay      │ 37 min      │ 11 min      │ 18 min            │
│ Blocks     │ 4           │ 3           │ 3                 │
│ Completion │ 100%        │ 100%        │ 91%               │
│ Overrun    │ 24%         │ 9%          │ 15%               │
│ Trains     │ 6           │ 2           │ 3                 │
│ Bundling   │ 1           │ 3           │ 2                 │
├────────────┴─────────────┴─────────────┴───────────────────┤
│ RECOMMENDED                                                  │
│ Plan B provides the lowest combined operational impact.      │
│                                                             │
│                    [Review Plan] [Approve]                  │
└─────────────────────────────────────────────────────────────┘
The blueprint explicitly requires top alternatives, objective breakdown, expected outcomes and Monte Carlo risk to be available for recommendation comparison.
________________________________________
27. Trade-off Controls
The planning UI should expose optimization preferences.
Example:
PLANNING PRIORITIES

Train Delay
██████████████████░░  High

Maintenance Completion
██████████████░░░░░░  Medium-High

Fewer Blocks
███████░░░░░░░░░░░░░  Medium

Robustness
██████████████░░░░░░  High
Changing these should clearly state:
“Changing planning priorities may change the recommended plan.”
The system should never silently alter the underlying safety constraints.
________________________________________
28. Hard vs Soft Constraint UX
This distinction should be visible.
HARD
Cannot be violated
Examples:
•	track conflict
•	crew qualification
•	possession limit
•	train safety conflict
SOFT
Preference
Examples:
•	preferred window
•	preferred crew
•	bundling preference
Example:
CONSTRAINT STATUS

✓ Section exclusivity
✓ Crew qualification
✓ Train movement safety
✓ Task dependency

⚠ Preferred maintenance window not selected
________________________________________
29. Simulation Workspace
Simulation should feel like a decision laboratory.
Not a chart page.
________________________________________
30. Scenario Builder
The user begins with:
LIVE STATE
State v1021
Then:
Create Scenario
Scenario B
Based on State v1021

Changes:
+ Move Block B102 from 01:00 → 03:00
+ Add S&T Task T117
- Remove Crew C04
________________________________________
31. Scenario Comparison
The screen should support side-by-side comparison:
LIVE PLAN          SCENARIO B
────────────       ─────────────
B102 01:00         B102 03:00

Delay: 11m         Delay: 18m
Risk: 9%           Risk: 13%
Tasks: 100%        Tasks: 100%
Trains: 2          Trains: 3
The user should never have to remember the original state mentally.
________________________________________
32. Simulation Result Design
Simulation output:
SCENARIO RESULT

Operational impact
───────────────────

Total delay             18 min
Affected trains         3
Maintenance completion   100%
Blocks                   3

Robustness
───────────────────

Overrun probability      13%
Plan violation           4%

Confidence
───────────────────

High
________________________________________
33. Monte Carlo Visualization
Do not overwhelm the user with 200 simulation traces.
Instead:
BLOCK B102

Completion distribution

P10 ────────●
Expected ────────●
P90 ─────────────────●

Overrun probability
██████░░░░░░░░░░ 9%
The 200 simulations remain available through an advanced detail view.
________________________________________
34. Disruption Workspace
Disruption UX must be radically different from ordinary planning.
The user needs:
What happened → what is affected → what should we do now?
________________________________________
35. Disruption Workflow
EVENT
  ↓
IMPACT
  ↓
PREDICTION
  ↓
RECOVERY OPTIONS
  ↓
SIMULATION
  ↓
RECOMMENDATION
  ↓
APPROVAL
________________________________________
36. Block Overrun Screen
Example:
┌────────────────────────────────────────────────────────────┐
│ ⚠ BLOCK B-102 OVERRUN                                     │
├────────────────────────────────────────────────────────────┤
│ Planned end       02:00                                   │
│ Current estimate  02:28                                   │
│ Overrun            +28 min                                │
│                                                            │
│ AFFECTED                                                 │
│                                                            │
│ 2 trains                                                 │
│ 1 downstream block                                       │
│ 3 maintenance dependencies                               │
│                                                            │
│ RAILMIND is generating recovery options...                │
└────────────────────────────────────────────────────────────┘
________________________________________
37. Recovery Recommendation
After computation:
RECOVERY RECOMMENDATION

Recommended Option
────────────────────────

Extend current possession
+
re-sequence Train 304
+
delay Block B104

Expected impact

Delay             +11 min
Additional trains 2
Recovery risk      Low

Alternative A
Reschedule B104
Delay: +19 min

Alternative B
Hold Train 304
Delay: +27 min
________________________________________
38. Track Unavailable Workflow
TRACK S4 UNAVAILABLE

Cause
Infrastructure incident

Impact
────────────────
4 trains
2 blocks
3 maintenance tasks

Plan invalidation
────────────────
B102  INVALID
B104  AFFECTED
T221  RESCHEDULE REQUIRED
Then:
Generate Recovery
________________________________________
39. Recovery UX Principle
Never simply say:
AI recommends Option A.
Instead:
RECOMMENDED OPTION A

Why?

✓ Maintains critical maintenance
✓ Lowest predicted train delay
✓ Lowest overrun risk
✓ Requires no additional crew

Why not B?

• +16 additional delay minutes
• affects 2 additional trains
________________________________________
40. Decision Workspace
The Decisions section becomes the institutional memory of RAILMIND.
It contains:
•	pending decisions
•	approved decisions
•	rejected decisions
•	modified decisions
•	expired recommendations
________________________________________
41. Recommendation Card
┌──────────────────────────────────────────────────────────┐
│ RECOMMENDATION R-102                                     │
│                                                          │
│ Approve Block B-102 · 01:00–02:30                       │
│                                                          │
│ Expected delay        11 min                            │
│ Overrun risk          9%                                │
│ Maintenance           100%                              │
│ Affected trains       2                                │
│                                                          │
│ Confidence            HIGH                              │
│                                                          │
│ [Review Evidence]   [Compare]   [Approve]               │
└──────────────────────────────────────────────────────────┘
________________________________________
42. Recommendation Detail
The detail screen should have five tabs:
Summary
What should happen.
Evidence
What the system used.
Constraints
What bounded the solution.
Alternatives
What else was possible.
Audit
What happened to the recommendation.
________________________________________
43. Explainability Design
Explainability should be layered.
Layer 1 — One sentence
Block B is recommended because it completes three high-priority tasks with the lowest predicted train impact.
Layer 2 — Evidence
3 critical tasks
2 affected trains
9% overrun risk
11 min predicted delay
Layer 3 — Constraint Trace
Section exclusivity
Crew capacity
Train movement
Task dependency
Window availability
Layer 4 — Technical
Solver:
CP-SAT

State:
v1021

Constraint set:
v1.2

Model:
duration@1.0
delay@1.0

Objective:
α5 β4 γ1 δ2 ε1
This allows executives, planners and engineers to consume the same decision at different depths.
________________________________________
44. Approval UX
Approval should be deliberately consequential.
The approval screen should say:
APPROVE PLAN B?

You are approving:

3 maintenance blocks
48 scheduled trains
11 min predicted total delay
9% maximum block overrun probability

State version:
v1021

Recommendation:
R-102

[Approve Plan]
[Modify]
[Reject]
The system should not use dark patterns to encourage approval.
________________________________________
45. Modification Workflow
If the user modifies an AI recommendation:
AI PLAN
   ↓
USER MODIFICATION
   ↓
RE-SIMULATE
   ↓
UPDATED IMPACT
   ↓
APPROVE
The system should never allow:
Modify
↓
Approve
without recalculating the consequences.
________________________________________
46. Decision Audit
Every decision should show:
Created
↓
Generated
↓
Simulated
↓
Recommended
↓
Reviewed
↓
Modified
↓
Approved
↓
Executed
↓
Outcome recorded
This gives RAILMIND a complete operational history.
________________________________________
47. Role-Specific UX
RAILMIND should not show every user the same interface.
________________________________________
48. Planner Experience
Primary goals:
•	maintenance prioritization
•	candidate blocks
•	bundling
•	scheduling
•	plan comparison
Default landing:
Maintenance / Block Planning
________________________________________
49. Controller Experience
Primary goals:
•	current train operations
•	active blocks
•	conflicts
•	disruptions
•	recovery
Default landing:
Command Center
________________________________________
50. Maintenance Supervisor Experience
Primary goals:
•	assigned tasks
•	crew
•	readiness
•	predicted duration
•	active blocks
Default landing:
Today’s Work
________________________________________
51. Approver Experience
Primary goals:
•	recommendations
•	trade-offs
•	risk
•	alternatives
•	authorization
Default landing:
Decision Queue
________________________________________
52. Senior Management Experience
Primary goals:
•	network health
•	operational impact
•	maintenance completion
•	major risks
•	scenario comparison
Default landing:
Executive Operations View
________________________________________
53. Responsive Design
RAILMIND should primarily target:
Desktop
Primary operational environment.
Large displays
Command center / operations room.
Tablet
Supervisor/planner field use.
Mobile should not attempt to replicate the entire desktop experience.
Instead it should provide:
•	alerts
•	decision review
•	recommendation approval
•	incident status
•	essential operational information
________________________________________
54. Visual Design Language
RAILMIND should have a professional industrial control-room aesthetic.
Avoid:
•	excessive gradients
•	neon colors
•	cartoon illustrations
•	giant rounded cards
•	excessive glassmorphism
•	AI robot imagery
•	excessive shadows
•	consumer-app visual language
Use:
•	restrained surfaces
•	strong typography
•	precise spacing
•	dense but readable information
•	clear hierarchy
•	subtle elevation
•	semantic status indicators
•	professional data visualization
________________________________________
55. Design System
Use a tokenized design system.
Typography
Spacing
Radius
Elevation
Borders
Status
Motion
Data visualization
The frontend should not allow individual developers to invent styles per screen.
________________________________________
56. Typography
Recommended hierarchy:
Display
32–40 px

Page title
24–28 px

Section
18–20 px

Body
14–16 px

Dense data
12–14 px

Metadata
11–12 px
Operational interfaces benefit from information density, but text must remain highly legible.
________________________________________
57. Color Semantics
Color must communicate meaning, not decoration.
Semantic states:
Normal
Attention
Warning
Critical
Unavailable
Predicted
Scenario
Approved
Rejected
Do not use color alone.
For example:
⚠ HIGH
rather than simply coloring a number yellow.
________________________________________
58. Data Visualization Principles
Every visualization must answer a question.
Bad:
Random graph
Good:
How does delay change if Block B102 moves by 2 hours?
Then show:
01:00 → 11 min
02:00 → 14 min
03:00 → 18 min
04:00 → 29 min
________________________________________
59. Density Principle
RAILMIND is professional operational software.
Therefore:
Information density is not the enemy. Unstructured information density is.
Use:
•	compact tables
•	grouping
•	progressive disclosure
•	side panels
•	filters
•	hierarchy
•	keyboard shortcuts
rather than removing useful information.
________________________________________
60. Progressive Disclosure
A user should initially see:
WHAT
WHY
IMPACT
ACTION
Advanced details are expandable.
Example:
Recommendation
     ↓
Why?
     ↓
Evidence
     ↓
Constraints
     ↓
Optimization details
     ↓
Model details
This allows both operational and technical users to use the product.
________________________________________
61. Interaction Principles
Principle 1
Every primary action has visible consequences.
Principle 2
Every AI recommendation has evidence.
Principle 3
Every destructive/consequential action requires confirmation.
Principle 4
Every scenario is visually separated from live state.
Principle 5
Every modified recommendation is re-evaluated.
Principle 6
Users can always understand where they are.
Principle 7
Users can always return to the current operational state.
________________________________________
62. Keyboard-First Operations
Professional users should not need the mouse for everything.
Potential shortcuts:
G C → Command Center
G M → Maintenance
G B → Block Planning
G S → Simulation
G D → Disruptions
G R → Recommendations

/ → Search

A → Approve
R → Reject
S → Simulate
Shortcuts should always be discoverable.
________________________________________
63. Global Search
RAILMIND should provide a command/search interface.
Search:
T-102
B-102
Train 201
Asset A-44
Section S4
Recommendation R-102
Results should identify object type.
Example:
T-102
Maintenance Task
S4 · Engineering
Critical
________________________________________
64. Contextual Side Panel
Avoid unnecessary navigation.
Clicking an object should open a side panel:
MAIN WORKSPACE
│
│
│                         ┌───────────────┐
│                         │ TASK T-102    │
│                         │               │
│                         │ details       │
│                         │ prediction    │
│                         │ recommendations│
│                         └───────────────┘
This preserves context.
________________________________________
65. Object-Centric UX
Every major RAILMIND entity should have a consistent object page.
Objects:
Train
Task
Asset
Block
Section
Incident
Plan
Scenario
Recommendation
Decision
Each object follows:
Overview
Timeline
Relationships
Predictions
Impact
History
Audit
This creates consistency across the entire application.
________________________________________
66. Operational Timeline
Every important entity should have a timeline.
Example:
T-102

08:30  Created
09:00  Classified HIGH
10:15  Priority increased → CRITICAL
11:00  Added to Plan B
12:30  Approved
01:00  Block started
02:28  Block overrun
02:29  Recovery triggered
This is extremely valuable for post-event analysis.
________________________________________
67. Workflow Architecture
RAILMIND should operate through several connected workflows.
________________________________________
68. Workflow A — Daily Planning
START OF PLANNING CYCLE
          ↓
Load operational state
          ↓
Reconcile PLAN vs ACTUAL
          ↓
Identify maintenance demand
          ↓
Predict risk/duration
          ↓
Prioritize tasks
          ↓
Identify candidate windows
          ↓
Generate bundled blocks
          ↓
Optimize train + maintenance
          ↓
Simulate
          ↓
Robustness analysis
          ↓
Generate alternatives
          ↓
Planner review
          ↓
Approver decision
          ↓
Approved plan
________________________________________
69. Workflow B — Planner Creates Plan
Select corridor
      ↓
Select planning horizon
      ↓
Review maintenance queue
      ↓
Select planning preferences
      ↓
Generate candidate plans
      ↓
Compare Plan A/B/C
      ↓
Inspect conflicts
      ↓
Inspect train impact
      ↓
Inspect robustness
      ↓
Modify if required
      ↓
Re-simulate
      ↓
Submit for approval
________________________________________
70. Workflow C — AI Recommendation
System detects opportunity
          ↓
Prediction models execute
          ↓
Rules validate feasibility
          ↓
CP-SAT generates solutions
          ↓
Simulation evaluates
          ↓
Monte Carlo evaluates robustness
          ↓
Decision engine ranks
          ↓
Explanation generated
          ↓
Recommendation created
          ↓
User reviews
________________________________________
71. Workflow D — Block Overrun
BLOCK ACTIVE
     ↓
Actual duration exceeds expected
     ↓
BLOCK_OVERRUN event
     ↓
State v1021 → v1022
     ↓
Affected trains identified
     ↓
Delay propagation predicted
     ↓
Affected/downstream windows identified
     ↓
Recovery CP-SAT
     ↓
Candidate plans
     ↓
Simulation
     ↓
Risk evaluation
     ↓
Rank
     ↓
Recommend
     ↓
Human approval
     ↓
Recovery plan
This mirrors the architecture defined in the blueprint.
________________________________________
72. Workflow E — Track Unavailable
TRACK_UNAVAILABLE
       ↓
Classify incident
       ↓
Find affected sections
       ↓
Traverse dependency graph
       ↓
Invalidate dependent plan
       ↓
Identify trains/tasks/blocks
       ↓
Generate recovery candidates
       ↓
Re-solve
       ↓
Simulate
       ↓
Compare
       ↓
Recommend
       ↓
Approve
________________________________________
73. Workflow F — User Modification
Recommendation
     ↓
Modify
     ↓
Constraint validation
     ↓
Prediction update
     ↓
Optimization/simulation
     ↓
New impact
     ↓
New recommendation version
     ↓
Approve
No stale recommendation may be approved after material modification.
________________________________________
74. Workflow G — Scenario Analysis
LIVE STATE
    ↓
Create Scenario
    ↓
Copy-on-write
    ↓
Modify variables
    ↓
Run simulation
    ↓
Evaluate
    ↓
Compare against LIVE
    ↓
Discard
OR
Promote to candidate plan
The underlying architecture requires scenarios to remain isolated from live state.
________________________________________
75. Workflow H — Decision Lifecycle
GENERATED
   ↓
SIMULATED
   ↓
RECOMMENDED
   ↓
REVIEWED
   ↓
APPROVED / MODIFIED / REJECTED
   ↓
EXECUTED
   ↓
OBSERVED
   ↓
OUTCOME RECORDED
________________________________________
76. Workflow I — Learning Loop
RAILMIND should eventually learn from operational outcomes.
Prediction
    ↓
Decision
    ↓
Execution
    ↓
Actual outcome
    ↓
Prediction error
    ↓
Historical record
    ↓
Model evaluation
    ↓
Future model improvement
This creates the long-term intelligence loop.
________________________________________
77. Empty States
Empty states must provide context.
Bad:
No data
Good:
NO ACTIVE DISRUPTIONS

The corridor is currently operating
without registered infrastructure disruptions.

Last checked
21:42
________________________________________
78. Loading States
Never display a generic spinner for long-running optimization.
Instead:
OPTIMIZING PLAN

✓ Loading operational state
✓ Evaluating 22 maintenance tasks
✓ Generating candidate blocks
✓ Solving train/block constraints
● Running robustness analysis
○ Ranking alternatives
This creates confidence.
________________________________________
79. Error States
Errors must explain:
What happened
What was affected
What can the user do
Example:
PLAN GENERATION FAILED

The optimization engine could not find a
feasible plan under the current constraints.

Possible cause:
Crew capacity conflict in Shift 2.

Suggested actions:
• Increase available crew
• Relax a soft preference
• Move Task T-121

[Review Constraints]
Never expose:
500 Internal Server Error
as the primary UX.
________________________________________
80. Trust Architecture
RAILMIND is an AI-assisted operational system.
Therefore the interface must actively establish trust.
Trust indicators:
Data freshness
Prediction confidence
State version
Model version
Simulation status
Constraint status
Recommendation evidence
________________________________________
81. Data Freshness
Every operational data source should indicate:
LIVE
Updated 12 sec ago
or:
STALE
Last updated 18 min ago
A user should never mistake old data for current state.
________________________________________
82. Prediction Confidence
Instead of pretending predictions are certain:
Predicted delay: 11 min
Confidence: High
Range: 8–16 min
This is especially important for duration and delay prediction.
________________________________________
83. Recommendation Confidence
Recommended levels:
HIGH
MEDIUM
LOW
Confidence should be based on system evidence rather than cosmetic AI branding.
________________________________________
84. AI Boundary UX
The interface must clearly distinguish:
SYSTEM FACT
PREDICTION
RECOMMENDATION
USER DECISION
Example:
ACTUAL
Block B102 is currently 28 min overdue.

PREDICTION
Train 304 may experience 11–16 min delay.

RECOMMENDATION
Re-sequence Train 304 and delay B104.

DECISION
Awaiting Controller approval.
This distinction is crucial.
________________________________________
85. No AI Theater
Avoid UI elements such as:
✨ AI Magic
🤖 Ask AI
AI Confidence 98%
unless they represent an actual system capability.
RAILMIND should communicate:
Intelligence through evidence.
not:
AI through branding.
________________________________________
86. Optional AI Assistant
If an LLM assistant is eventually included, it should exist as a secondary interface.
Example:
RAILMIND COPILOT

User:
Why was Block B102 recommended?

RAILMIND:
B102 completes three high-priority tasks while
producing the lowest predicted train impact.

[View Evidence]
The assistant should never become the primary operational interface.
________________________________________
87. AI Assistant Guardrails
The assistant can:
•	explain
•	summarize
•	navigate
•	answer questions using system data
•	compare plans
•	surface evidence
The assistant cannot:
•	override constraints
•	invent operational state
•	modify live state without workflow authorization
•	approve a plan
•	control trains
•	generate unsupported numerical claims
________________________________________
88. Accessibility
Target:
WCAG 2.2 AA
Requirements:
•	keyboard navigation
•	visible focus
•	semantic HTML
•	sufficient contrast
•	non-color status communication
•	accessible tables
•	screen-reader labels
•	scalable typography
________________________________________
89. Performance UX
The UI should distinguish:
Instant
Navigation, filters, local interactions.
Fast
Data retrieval.
Compute
Optimization/simulation.
Compute operations should have explicit progress.
Example:
Optimization
~4.2 sec

Simulation
~1.1 sec

Robustness
~0.8 sec
________________________________________
90. Professional Motion Design
Motion should communicate:
•	state change
•	loading
•	transition
•	causality
Avoid decorative animation.
Examples:
PLAN → ACTUAL
should transition clearly.
When a block overruns, the timeline should visibly update affected objects.
________________________________________
91. Notification Center
The notification center should distinguish:
ACTION REQUIRED
WATCH
SYSTEM
INFORMATION
Example:
ACTION REQUIRED
2 recovery decisions pending

WATCH
Task T-102 approaching deadline

SYSTEM
Optimization engine healthy
________________________________________
92. Saved Views
Professional users should be able to save:
My Critical Maintenance
Today's Blocks
High-Risk Assets
Affected Trains
Pending Decisions
This reduces repetitive filtering.
________________________________________
93. Role-Based Default Views
Each user receives a meaningful starting workspace.
Planner
→ Maintenance Queue

Controller
→ Command Center

Supervisor
→ Active Work

Approver
→ Decision Queue

Manager
→ Operations Overview
________________________________________
94. Design System Components
The RAILMIND design system should define reusable:
Navigation
•	Sidebar
•	Top bar
•	Breadcrumb
•	Workspace tabs
Data
•	Data table
•	Timeline
•	KPI
•	Metric
•	Status badge
•	Confidence indicator
Operations
•	Alert
•	Incident card
•	Block card
•	Train card
•	Task card
Intelligence
•	Prediction panel
•	Recommendation card
•	Evidence panel
•	Alternative comparison
Planning
•	Timeline
•	Constraint indicator
•	Scenario control
•	Plan comparison
Decisions
•	Approval panel
•	Audit timeline
•	Decision history
________________________________________
95. Design Tokens
Create tokens before screen implementation.
Example:
--surface-primary
--surface-secondary
--surface-elevated

--text-primary
--text-secondary
--text-muted

--border-default
--border-strong

--status-normal
--status-attention
--status-warning
--status-critical

--spacing-1
--spacing-2
--spacing-3
...
No screen should contain arbitrary styling values wherever avoidable.
________________________________________
96. UX Architecture by Information Depth
RAILMIND should have four levels.
LEVEL 1
Operational overview

LEVEL 2
Decision workspace

LEVEL 3
Evidence

LEVEL 4
Technical provenance
This prevents the system from being simultaneously too simplistic for engineers and too complicated for operational users.
________________________________________
97. Core “Decision Card”
The most important reusable component in RAILMIND should be the:
Decision Card
It contains:
WHAT
Recommended action

WHY
Reason

IMPACT
Expected consequence

RISK
Uncertainty

ALTERNATIVES
What else could happen

ACTION
Approve / Modify / Reject
This component can appear in:
•	Command Center
•	Block Planning
•	Disruption
•	Simulation
•	Decisions
________________________________________
98. Signature UX: “Why This Plan?”
Every generated plan should have a prominent:
Why this plan?
button.
Opening it:
WHY THIS PLAN?

1. Completes 4 critical tasks
2. Avoids 3 train conflicts
3. Bundles 3 departmental tasks
4. Uses available qualified crew
5. Produces 9% overrun probability
6. Produces 11 min predicted delay

Alternative Plan C:
+26 min additional delay
+15% overrun risk
This should become one of RAILMIND’s defining UX moments.
________________________________________
99. Signature UX: “What Changes?”
Whenever a user changes something:
WHAT CHANGES?

Moving B102 from 01:00 → 03:00

Train delay
11 → 18 min

Affected trains
2 → 3

Overrun risk
9% → 13%

Maintenance completion
100% → 100%
This turns RAILMIND from a passive dashboard into an interactive decision system.
________________________________________
100. Signature UX: “Impact Map”
When an incident occurs:
TRACK S4
   │
   ├── Train 201
   ├── Train 304
   ├── Block B102
   ├── Task T221
   └── Resource C04
The user can visually understand the dependency chain.
________________________________________
101. Signature UX: “Decision Replay”
After an event, users can replay:
State v1021
      ↓
Block B102 active
      ↓
Overrun detected
      ↓
State v1022
      ↓
Recovery candidates
      ↓
Plan B selected
      ↓
Approved
This is useful for:
•	auditing
•	training
•	incident review
•	management
•	future model improvement
________________________________________
102. Operational Workflow Master Map
                       RAILMIND
                           │
                    CURRENT STATE
                           │
              ┌────────────┴────────────┐
              │                         │
          PLANNED                    ACTUAL
              │                         │
              └────────────┬────────────┘
                           ↓
                    STATE RECONCILIATION
                           ↓
                    INTELLIGENCE LAYER
                           │
          ┌────────────────┼────────────────┐
          ↓                ↓                ↓
       PRIORITY         DURATION           DELAY
          │                │                │
          └────────────────┼────────────────┘
                           ↓
                     RULES ENGINE
                           ↓
                   CANDIDATE GENERATION
                           ↓
                     CP-SAT OPTIMIZER
                           ↓
                    CANDIDATE PLANS
                           ↓
                      SIMULATION
                           ↓
                    MONTE CARLO
                           ↓
                  DECISION INTELLIGENCE
                           ↓
                  ┌────────┴────────┐
                  ↓                 ↓
              PLAN A              PLAN B
                  │                 │
                  └────────┬────────┘
                           ↓
                     HUMAN REVIEW
                           ↓
                  APPROVE / MODIFY / REJECT
                           ↓
                       EXECUTION
                           ↓
                     ACTUAL STATE
                           ↓
                      MONITORING
                           ↓
                      DISRUPTION?
                       /       \
                     NO         YES
                     │           │
                     │       IMPACT ANALYSIS
                     │           ↓
                     │       RECOVERY OPTIONS
                     │           ↓
                     └────→ RE-OPTIMIZE
                                 ↓
                              APPROVE
                                 ↓
                              EXECUTE
                                 ↓
                            NEW STATE
________________________________________
103. UX State Machine
The interface itself should follow the operational state machine:
NORMAL
  ↓
ATTENTION
  ↓
INVESTIGATING
  ↓
OPTIONS_AVAILABLE
  ↓
SIMULATING
  ↓
RECOMMENDATION_READY
  ↓
AWAITING_APPROVAL
  ↓
APPROVED
  ↓
EXECUTING
  ↓
MONITORING
Exception:
MONITORING
    ↓
DISRUPTION
    ↓
RECOVERY_REQUIRED
    ↓
RECOVERY_OPTIONS
    ↓
AWAITING_APPROVAL
________________________________________
104. User Journey — Planner
Login
 ↓
Command Center
 ↓
Critical maintenance alert
 ↓
Open Maintenance
 ↓
Inspect Task T102
 ↓
View risk and duration
 ↓
Open Block Planning
 ↓
Generate plans
 ↓
Compare A/B/C
 ↓
Inspect "Why this plan?"
 ↓
Adjust planning preference
 ↓
Re-simulate
 ↓
Submit Plan B
 ↓
Approver review
________________________________________
105. User Journey — Controller
Login
 ↓
Command Center
 ↓
Track S4 unavailable
 ↓
Open disruption
 ↓
View impact map
 ↓
Review affected trains
 ↓
Generate recovery
 ↓
Compare options
 ↓
Review predicted delays
 ↓
Approve recovery
 ↓
Monitor network
________________________________________
106. User Journey — Approver
Login
 ↓
Decision Queue
 ↓
Recommendation R102
 ↓
Summary
 ↓
Evidence
 ↓
Alternatives
 ↓
Risk
 ↓
Audit context
 ↓
Approve / Modify / Reject
 ↓
Decision recorded
________________________________________
107. Design Quality Standards
Every major screen must satisfy:
Clarity
Can a new user understand the screen within 5–10 seconds?
Hierarchy
Is the most important information visually dominant?
Actionability
Can the user determine what to do next?
Explainability
Can the user understand why the system reached the recommendation?
Safety
Can the user distinguish live state from prediction/scenario?
Traceability
Can the user find the relevant decision history?
Density
Does the screen provide enough information without becoming chaotic?
________________________________________
108. Anti-Patterns — Explicitly Forbidden
RAILMIND should NOT become:
Dashboard Soup
20 KPI cards with no decision path.
AI Chatbot First
Chat interface replacing operational workflows.
Dark AI
Recommendations without evidence.
Color Explosion
Every metric having a different bright color.
Fake 3D Digital Twin
Decorative 3D railway visualization without operational value.
Button Farm
Every operation represented as a button.
Modal Hell
Every action opening another modal.
Hidden State
Scenario and live state visually indistinguishable.
Magic Optimization
“AI optimized your plan” with no explanation.
Static Prototype
Screens displaying hardcoded numbers disconnected from backend state.
________________________________________
109. UX Architecture and Technical Architecture Alignment
The UI must directly correspond to backend concepts.
Backend	UX
State Engine	State indicator
PLAN	Planned layer
ACTUAL	Live layer
PREDICTION	Forecast layer
SCENARIO	Scenario workspace
ML	Prediction panels
Rules	Constraint panel
CP-SAT	Plan generation
Simulation	Scenario lab
Monte Carlo	Robustness panel
Decision Engine	Recommendation
Audit	Decision timeline
Events	Attention queue
Recovery	Disruption workspace
This prevents the UI from becoming disconnected from the technical architecture.
________________________________________
110. Design-to-Engineering Contract
Frontend and backend teams should agree on these concepts before implementation:
State
Entity
Prediction
Recommendation
Scenario
Plan
Decision
Event
Alert
Constraint
Impact
Each must have a stable API representation.
________________________________________
111. Frontend Route Architecture
Recommended:
/
├── command-center
│
├── operations
│   ├── trains
│   ├── network
│   └── assets
│
├── maintenance
│   ├── queue
│   └── [task]
│
├── planning
│   ├── blocks
│   ├── plans
│   └── [plan]
│
├── simulation
│   ├── scenarios
│   └── [scenario]
│
├── disruptions
│   ├── active
│   └── [incident]
│
├── decisions
│   ├── queue
│   └── [recommendation]
│
├── audit
│
└── settings
________________________________________
112. Design System Implementation
Recommended frontend stack:
Next.js
React
TypeScript
Tailwind CSS
shadcn/ui
TanStack Query
Zustand
Recharts
React Hook Form
Zod
The underlying technical architecture already specifies React + Next.js + TypeScript for Tier 1.
________________________________________
113. UX Telemetry
The UI should eventually measure:
Time to first decision
Time to inspect recommendation
Recommendation acceptance rate
Modification rate
Scenario creation rate
Plan comparison usage
Alert acknowledgement time
Recovery decision time
This helps determine whether RAILMIND actually improves decision-making.
________________________________________
114. Product-Level UX Metrics
The most important UX metric is not:
“How many screens did the user visit?”
It is:
How quickly and confidently can the user move from operational problem → informed decision?
Therefore track:
Problem detected
      ↓
Problem understood
      ↓
Options generated
      ↓
Option evaluated
      ↓
Decision made
________________________________________
115. North Star UX Metric
Time to Confident Decision
Measure:
TCD =
Time from actionable event
to authorized decision
For example:
Track unavailable
21:10

Recovery options ready
21:10:08

Operator review
21:10:35

Approval
21:11:02

Time to confident decision
52 seconds
This is far more meaningful than generic frontend performance metrics.
________________________________________
116. UX Maturity Roadmap
Stage 1
Operational visibility.
Command Center
Maintenance
Blocks
Trains
Stage 2
Decision intelligence.
Recommendations
Alternatives
Explainability
Simulation
Stage 3
Adaptive operations.
Disruption
Recovery
Continuous replanning
Stage 4
Enterprise intelligence.
Multi-division
Cross-zone
Advanced analytics
Long-term decision intelligence
________________________________________
117. The RAILMIND Experience
The complete experience should feel like:
                 ┌───────────────────┐
                 │    WHAT'S GOING   │
                 │       ON?         │
                 └─────────┬─────────┘
                           ↓
                 ┌───────────────────┐
                 │    WHAT MATTERS?  │
                 └─────────┬─────────┘
                           ↓
                 ┌───────────────────┐
                 │  WHAT CAN WE DO?  │
                 └─────────┬─────────┘
                           ↓
                 ┌───────────────────┐
                 │  WHAT WILL HAPPEN?│
                 └─────────┬─────────┘
                           ↓
                 ┌───────────────────┐
                 │   WHY THIS PLAN?  │
                 └─────────┬─────────┘
                           ↓
                 ┌───────────────────┐
                 │    HUMAN DECIDES  │
                 └─────────┬─────────┘
                           ↓
                 ┌───────────────────┐
                 │   SYSTEM ADAPTS   │
                 └───────────────────┘
________________________________________
118. Final UX Design Principle
RAILMIND should not attempt to impress users with visual complexity.
It should impress them with clarity under complexity.
The railway is complicated.
The UI should not hide that complexity.
Instead:
RAILMIND should absorb the complexity and present the decision.
A planner should not need to understand CP-SAT to use RAILMIND.
A controller should not need to understand XGBoost to trust a delay prediction.
A senior decision-maker should not need to inspect 200 Monte Carlo runs.
But when someone asks:
“Why did RAILMIND recommend this?”
the system must be able to answer—immediately, visually, and with evidence.
________________________________________
119. Final Product Experience
The ideal RAILMIND interaction is:
SEE
↓
UNDERSTAND
↓
EXPLORE
↓
SIMULATE
↓
COMPARE
↓
DECIDE
↓
APPROVE
↓
MONITOR
↓
RECOVER
Not:
Dashboard
↓
Click AI button
↓
Get prediction
↓
Done
RAILMIND’s UI therefore becomes the operational interface to its decision-intelligence architecture.
The backend provides intelligence.
The UI provides understanding.
The workflow provides control.
The human provides authorization.
Together:
RAILMIND does not replace the railway operator. It gives the operator a better way to understand, evaluate and act on the railway.
END OF DOCUMENT
