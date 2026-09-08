# RailMind — Multi-Agent Development Workflow

This document establishes the official branching structure, agent ownership boundaries, contract governance rules, and integration workflows for multi-agent development across the RailMind project.

---

## 1. Branch Structure & Ownership

RailMind uses three specialized development agents operating in parallel on dedicated Git branches originating from the stable `main` branch:

```text
main
│
├── antigravity/core
├── opencode/frontend
└── freebuff/engine
```

### Branch Responsibilities

| Branch | Agent | Primary Ownership |
|---|---|---|
| `main` | Integrated / Stable | Integrated stable RailMind release branch. No direct unvalidated commits. |
| `antigravity/core` | **Antigravity** | Architecture lead, backend (`backend/`), API endpoints, services, repositories, persistence, system integration. |
| `opencode/frontend` | **OpenCode** | Frontend (`frontend/`), UI/UX components, design system, client-side views, and frontend API consumption. |
| `freebuff/engine` | **Freebuff** | Intelligence and algorithmic logic (`engine/`), constraint engines, priority scoring, mathematical optimization (CP-SAT/OR-Tools), simulation, forecasting, and recovery algorithms. |

---

## 2. Directory Ownership Boundaries

```text
RailMind/
│
├── backend/              → Antigravity (Backend / Core)
│
├── frontend/             → OpenCode (Frontend / UI / UX)
│
├── engine/               → Freebuff (Intelligence / Optimization / Algorithms)
│
├── contracts/            → SHARED & PROTECTED (Canonical Domain & API Contracts)
│
├── docs/                 → Coordinated / Shared Documentation
│
├── fixtures/             → Coordinated / Shared Test Scenarios
│
├── scripts/              → Coordinated / Shared Automation Utilities
│
└── tests/                → Coordinated / Integration Test Suites
```

---

## 3. Canonical Contracts Protection Rule

The `contracts/` directory (along with `frontend/contracts/`) is the **single canonical source of truth** for all domain types, branded identifiers, enums, error models, and API transport envelopes.

```text
                    contracts/
                   /          \
                  /            \
                 ▼              ▼
          Antigravity        Freebuff
           Backend            Engine
              │                 │
              └───────┬─────────┘
                      │
                      ▼
                  OpenCode
                  Frontend
```

* **Contract Invariance:** No individual agent may unilaterally or arbitrarily modify canonical contracts.
* **Coordination Required:** Any contract evolution requires multi-agent coordination, backward compatibility checks, and updating all corresponding consumers across frontend, backend, and engine layers.

---

## 4. Integration & Merging Workflow

All agents follow a rigorous verification workflow before pushing or merging:

```text
Feature Development (on agent branch)
     ↓
Backend Tests (`pytest`)
     ↓
Frontend Verification (`typecheck`, `lint`, `test`, `build`)
     ↓
Canonical Contract Validation
     ↓
Atomic Commit with Semantic Message
     ↓
Push to Agent Remote Branch (`origin/<agent-branch>`)
     ↓
Review & Verification
     ↓
Merge into `main`
     ↓
Other Agent Branches Synchronize (`git merge origin/main` / `git rebase origin/main`)
```

### Main Branch Governance
* `main` represents production-grade, tested, working integration state.
* Do not push unverified, breaking, or incomplete code to `main`.
* Individual agents test in isolation on their designated branch before integrating into `main`.

---

## 5. Feature Branch Naming Conventions

For targeted sub-features or phase-specific tasks, agents may create scoped feature branches off their respective agent branch or `main`:

```text
antigravity/<feature-name>    (e.g., antigravity/p13-database)
opencode/<feature-name>       (e.g., opencode/command-center-workspace)
freebuff/<feature-name>       (e.g., freebuff/p09-constraint-engine)
```