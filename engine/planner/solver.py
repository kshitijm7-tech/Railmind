"""§17 solver orchestration (E09) — CP-SAT solve + E03 evaluation.

The engine pipeline's missing piece: given a ``PlannerInput`` (§17.1–§17.3
model data with E02 priority results and E09 §16.3 delay evidence), produce
the best plan plus near-optimal alternatives under the §17.4 hard
constraints, each evaluated by **E03's exact §17.5 evaluator** — the planner
never re-implements objective semantics (TRD §73: "CP-SAT optimizes"; E03
owns the objective).

Solver-side objective encoding (integer-scaled ×100, exact at E03 level):
  per window y[w]:   γ·1 + δ·overrun_risk(w)·100 + α·Σ_r delay_pred(w,r)·100
  per assignment x[t,w]: −ε·bundle_bonus(w)·100        (§17.5 ε is over x!)
The β term is task-level (unscheduled·priority) and belongs to E03's
evaluation of the extracted solution — CP-SAT steers the block/assignment
search; E03 ranks the candidates exactly.

Tier-1 delay reading (documented): §17.5 counts delay_pred(w, r) "for every
activated window w whose active train conflicts are unresolved (not fully
absorbed by re-sequencing)". Tier 1 has no train re-sequencing model, so
every activated window's predicted delay counts — the conservative reading.

k-best enumeration (TRD §70 DoD: "alternatives generated"): after each
solve, a no-good cut forbids exactly the returned activation pattern; the
next round yields the next-best *distinct* pattern. Deterministic:
num_workers=1, explicit random_seed (blueprint §26, TRD §67).

Infeasibility is honest (§11): the c1 slack (§17.3) exists so the model
always stays feasible — an unreachable deadline (c9) forces the task
*unscheduled* with its true β cost rather than a solver failure.
``PlannerError`` is raised only when no solution is found inside the
time budget (``TIMEOUT_NO_PLAN``) or a defensive INFEASIBLE occurs.

Time budget (TRD §65/§26): ``timeout_seconds`` is the TOTAL budget across
all k-best rounds; each round receives the remaining time. A round that
times out stops the enumeration (already-found candidates are kept and
the evidence status reports FEASIBLE, never a silently truncated solve).
"""

import time
from datetime import timedelta
from typing import Dict, FrozenSet, List, Optional, Tuple

from ortools.sat.python import cp_model

from engine._version import PLANNER_MODEL_ID, PLANNER_MODEL_VERSION
from engine.optimization.evaluation import ObjectiveEvaluator
from engine.optimization.inputs import BlockActivation, CandidateSolution, TaskAssignment
from engine.planner.configuration import PlannerConfig
from engine.planner.cpsat_model import (
    C3_QUALIFICATION,
    C4_CREW_CAPACITY,
    C6_DURATION_FEASIBILITY,
    C7_WINDOW_BOUNDS,
    C8_PRECEDENCE,
    C9_DEADLINE,
    PlannerModel,
)
from engine.planner.errors import PlannerError
from engine.planner.inputs import PlannerInput
from engine.planner.result import (
    BlockActivationResult,
    ConstraintTraceEntry,
    GeneratedPlan,
    PlannerResult,
    SolveEvidence,
    TaskAssignmentResult,
)

_CP_SAT_SOLVER_NAME = "cpsat"
STATUS_OPTIMAL = "OPTIMAL"
STATUS_FEASIBLE = "FEASIBLE"
STATUS_INFEASIBLE = "INFEASIBLE"
STATUS_TIMEOUT_NO_PLAN = "TIMEOUT_NO_PLAN"


def _ortools_version() -> str:
    try:
        import ortools

        return str(getattr(ortools, "__version__", "unknown"))
    except Exception:  # pragma: no cover — version probe only
        return "unknown"


class CpSatPlanner:
    """The §17 CP-SAT optimization engine (TRD §73: 'CP-SAT optimizes')."""

    def __init__(self, config: PlannerConfig = None):
        self._config = config or PlannerConfig()

    @property
    def config(self) -> PlannerConfig:
        return self._config

    def get_version(self) -> str:
        return f"{PLANNER_MODEL_ID}@{PLANNER_MODEL_VERSION}"

    # --- public API ---------------------------------------------------------

    def plan(self, data: PlannerInput) -> PlannerResult:
        cfg = self._config
        started = time.perf_counter()
        evaluator = ObjectiveEvaluator(cfg.objective)

        delay_totals: Dict[str, float] = {
            window_id: sum(view.values())
            for window_id, view in data.delay_predictions.items()
        }

        candidates, all_optimal = self._solve_candidates(data, cfg, delay_totals)
        if not candidates:
            raise PlannerError(
                "no feasible plan found inside the configured time budget "
                f"({cfg.timeout_seconds}s) — solver status: {STATUS_TIMEOUT_NO_PLAN}"
            )

        extracted = [
            self._extract_and_evaluate(data, extract, evaluator, index)
            for index, extract in enumerate(candidates)
        ]
        # Rank by E03's semantics (total, then enumeration index — stable),
        # THEN renumber ids by rank so ``best_plan_id`` always ends in
        # ``-alt0`` and consumers get canonical, position-stable ids.
        extracted.sort(
            key=lambda p: (
                p.objective.total_objective,
                int(p.plan_id.rsplit("-alt", 1)[1]),
            )
        )
        plans: List[GeneratedPlan] = []
        for rank, plan in enumerate(extracted):
            base = data.plan_ref or "plan"
            canonical_id = f"{base}-alt{rank}"
            plans.append(
                plan.model_copy(
                    update={"plan_id": canonical_id, "objective": plan.objective.model_copy(update={"plan_id": canonical_id})}
                )
            )

        wall_time_ms = (time.perf_counter() - started) * 1000.0
        evidence = SolveEvidence(
            solver=_CP_SAT_SOLVER_NAME,
            solver_version=_ortools_version(),
            random_seed=cfg.random_seed,
            timeout_seconds=cfg.timeout_seconds,
            status=STATUS_OPTIMAL if all_optimal else STATUS_FEASIBLE,
            wall_time_ms=wall_time_ms,
            objective_weights=cfg.objective.objective_weights(),
        )
        return PlannerResult(
            plans=plans,
            best_plan_id=plans[0].plan_id,
            evidence=evidence,
            metadata={},
        )

    # --- solving ------------------------------------------------------------

    def _solve_candidates(
        self,
        data: PlannerInput,
        cfg: PlannerConfig,
        delay_totals: Dict[str, float],
    ) -> Tuple[List[dict], bool]:
        """k-best enumeration of distinct activation patterns via no-good
        cuts. Returns (extracted candidates, all_rounds_optimal)."""
        candidates: List[dict] = []
        forbidden: List[FrozenSet[str]] = []
        all_optimal = True
        budget_started = time.perf_counter()

        # Reserve a slice of the budget for extraction + E03 evaluation so
        # the whole run completes inside ``timeout_seconds`` (TRD §65: the
        # configured budget is the run's, not just one solve's).
        EVALUATION_RESERVE_SECONDS = 0.5

        # alternative_count = plans ALONGSIDE the best (PRD §29: "a
        # recommended plan plus alternatives"; config docstring) — so the
        # enumeration runs alternative_count + 1 rounds total.
        for _round in range(cfg.alternative_count + 1):
            elapsed = time.perf_counter() - budget_started
            remaining = cfg.timeout_seconds - elapsed - EVALUATION_RESERVE_SECONDS
            if remaining <= 0 and candidates:
                all_optimal = False
                break  # budget exhausted — keep what the rounds found
            model = PlannerModel(data)
            cp = model.model

            # Objective: window-level terms on y[w], assignment-level ε on x.
            terms = []
            for window in data.windows:
                y = model.y[window.window_id]
                cost = cfg.objective.block_count_weight
                cost += cfg.objective.overrun_risk_weight * window.overrun_risk * 100
                cost += cfg.objective.train_delay_weight * delay_totals.get(
                    window.window_id, 0.0
                )
                terms.append(int(round(cost)) * y)
            for window in data.windows:
                reward = int(
                    round(cfg.objective.bundling_weight * window.bundle_bonus * 100)
                )
                if reward:
                    for task in data.tasks:
                        terms.append(-reward * model.x[(task.task_id, window.window_id)])
            # β term (§17.5): unscheduled_t · priority_t — makes the solver's
            # internal optimum align with E03's exact §17.5 total, so an
            # activated window never idles an assignable task.
            for task in data.tasks:
                beta_cost = int(
                    round(
                        cfg.objective.unscheduled_priority_weight
                        * task.priority.score
                        * 100
                    )
                )
                if beta_cost:
                    terms.append(beta_cost * model.unscheduled[task.task_id])
            if terms:
                cp.Minimize(sum(terms))

            # No-good cuts: forbid every previously returned activation
            # pattern (active-set form: Σ_{active}(1−y) + Σ_{inactive}(y) ≥ 1).
            window_ids = [w.window_id for w in data.windows]
            for pattern in forbidden:
                cut_terms = []
                for wid in window_ids:
                    y = model.y[wid]
                    cut_terms.append(1 - y if wid in pattern else y)
                cp.Add(sum(cut_terms) >= 1)

            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = max(0.05, remaining)
            solver.parameters.num_workers = 1
            solver.parameters.random_seed = cfg.random_seed
            status = solver.Solve(cp)

            if status == cp_model.OPTIMAL:
                pass
            elif status == cp_model.FEASIBLE:
                all_optimal = False
            elif status == cp_model.INFEASIBLE:
                # With the §17.3 slack the model is always satisfiable; this
                # branch is defensive (e.g. a malformed cut) — surface it.
                if not candidates:
                    raise PlannerError(
                        "planning instance is infeasible under the §17.4 "
                        "hard constraints; no plan exists"
                    )
                break
            else:
                # UNKNOWN / budget hit mid-solve: enumeration stops with what
                # exists; the caller sees FEASIBLE evidence, never a silent
                # truncation of the plan itself.
                all_optimal = False
                break

            y_values = {
                w.window_id: solver.Value(model.y[w.window_id]) for w in data.windows
            }
            x_values = {key: solver.Value(var) for key, var in model.x.items()}

            # Timing-tightening pass: fix the pattern (y/x) and minimize
            # Σ span so possessions are exactly as long as the work (c6 is a
            # ≥ constraint; without this pass the solver may leave a
            # full-window possession for a few minutes of work). c5
            # no-overlap still applies, so contended sections distribute.
            for wid in y_values:
                cp.Add(model.y[wid] == y_values[wid])
            for key, value in x_values.items():
                cp.Add(model.x[key] == value)
            cp.Minimize(sum(model.spans.values()))
            timing_status = solver.Solve(cp)
            if timing_status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                start_values = {
                    w.window_id: solver.Value(model.starts[w.window_id])
                    for w in data.windows
                }
                end_values = {
                    w.window_id: solver.Value(model.ends[w.window_id])
                    for w in data.windows
                }
            else:  # pragma: no cover — tightened model is always feasible
                start_values = {
                    w.window_id: solver.Value(model.starts[w.window_id])
                    for w in data.windows
                }
                end_values = {
                    w.window_id: solver.Value(model.ends[w.window_id])
                    for w in data.windows
                }

            model._last_solution = (y_values, x_values, start_values, end_values)
            candidates.append(
                {
                    "y": y_values,
                    "x": x_values,
                    "starts": start_values,
                    "ends": end_values,
                    "trace": _binding_facts(model, data),
                }
            )
            forbidden.append(
                frozenset(w for w, v in y_values.items() if v)
            )

        return candidates, all_optimal

    # --- extraction + E03 evaluation -----------------------------------------

    def _extract_and_evaluate(
        self,
        data: PlannerInput,
        extract: dict,
        evaluator: ObjectiveEvaluator,
        index: int,
    ) -> GeneratedPlan:
        y_values: Dict[str, int] = extract["y"]
        x_values: Dict[Tuple[str, str], int] = extract["x"]
        start_values: Dict[str, int] = extract["starts"]
        end_values: Dict[str, int] = extract["ends"]
        zero = min((w.earliest_start for w in data.windows), default=None)

        assignments: List[TaskAssignmentResult] = []
        solution_assignments: List[TaskAssignment] = []
        unscheduled_ids: List[str] = []

        for task in data.tasks:
            assigned_window = next(
                (
                    w.window_id
                    for w in data.windows
                    if x_values.get((task.task_id, w.window_id), 0)
                ),
                None,
            )
            if assigned_window is None:
                unscheduled_ids.append(task.task_id)
            # E03's β term requires the real PriorityResult for unscheduled
            # tasks — the planner never substitutes an invented score.
            solution_assignments.append(
                TaskAssignment(
                    task_id=task.task_id,
                    unscheduled=assigned_window is None,
                    priority=task.priority,
                )
            )
            assignments.append(
                TaskAssignmentResult(task_id=task.task_id, window_id=assigned_window)
            )

        blocks: List[BlockActivationResult] = []
        solution_blocks: List[BlockActivation] = []
        for window in data.windows:
            if not y_values.get(window.window_id, 0):
                continue
            assigned = [
                t
                for t in data.tasks
                if x_values.get((t.task_id, window.window_id), 0)
            ]
            blocks.append(
                BlockActivationResult(
                    window_id=window.window_id,
                    section_id=window.section_id,
                    start=zero + timedelta(minutes=start_values[window.window_id]),
                    end=zero + timedelta(minutes=end_values[window.window_id]),
                    assigned_task_ids=[t.task_id for t in assigned],
                    assigned_work_minutes=float(
                        sum(t.duration_minutes for t in assigned)
                    ),
                    delay_evidence=data.delay_results.get(window.window_id),
                )
            )
            solution_blocks.append(
                BlockActivation(
                    window_id=window.window_id,
                    bundle_bonus=window.bundle_bonus,
                    overrun_risk=window.overrun_risk,
                )
            )

        total_delay = sum(
            sum(view.values())
            for window_id, view in data.delay_predictions.items()
            if y_values.get(window_id, 0)
        )

        base_id = data.plan_ref or "plan"
        solution = CandidateSolution(
            plan_id=f"{base_id}-alt{index}",
            assignments=solution_assignments,
            blocks=solution_blocks,
            total_train_delay_minutes=total_delay,
        )
        breakdown = evaluator.evaluate(solution)

        return GeneratedPlan(
            plan_id=solution.plan_id,
            assignments=assignments,
            blocks=blocks,
            unscheduled_task_ids=unscheduled_ids,
            objective=breakdown,
            constraint_trace=extract.get("trace", []),
        )


def _binding_facts(model: PlannerModel, data: PlannerInput) -> List[ConstraintTraceEntry]:
    """Derive binding/active constraint roles from solver facts.

    ``binding`` = demonstrably shaped the returned solution (a solver-
    derivable fact); ``active`` = enforced but not proven tight. Structural
    constraints (c1/c2/c5) are always ``active``.
    """
    by_id = {t["constraint_id"]: t for t in model.traces}
    facts: List[ConstraintTraceEntry] = []

    def _entry(constraint_id: str, binding: bool) -> ConstraintTraceEntry:
        template = by_id[constraint_id]
        return ConstraintTraceEntry(
            constraint_id=constraint_id,
            description=template["description"],
            role="binding" if binding else "active",
        )

    solved = getattr(model, "_last_solution", None)
    if solved is None:
        return [_entry(cid, False) for cid in by_id]
    y_values, x_values, start_values, end_values = solved

    # c3 binding: at least one task×window pair disqualified by qualification.
    c3_binding = any(
        task.department not in window.qualified_departments
        for task in data.tasks
        for window in data.windows
    )
    if C3_QUALIFICATION in by_id:
        facts.append(_entry(C3_QUALIFICATION, c3_binding))

    # c4 binding: an activated window at its department's crew limit.
    c4_binding = False
    pools: Dict[str, int] = {}
    for pool in data.crew_pools:
        pools[pool.department] = max(pools.get(pool.department, 0), pool.available_crew)
    for window in data.windows:
        if not y_values.get(window.window_id, 0):
            continue
        per_dept: Dict[str, int] = {}
        for task in data.tasks:
            if x_values.get((task.task_id, window.window_id), 0):
                per_dept[task.department] = (
                    per_dept.get(task.department, 0) + task.crew_size
                )
        if any(
            dept in pools and crew >= pools[dept]
            for dept, crew in per_dept.items()
        ):
            c4_binding = True
            break
    if C4_CREW_CAPACITY in by_id:
        facts.append(_entry(C4_CREW_CAPACITY, c4_binding))

    # c6 binding: an activated window whose span equals its workload
    # (the assigned work pins the block length to the exact minute).
    c6_binding = False
    for window in data.windows:
        if not y_values.get(window.window_id, 0):
            continue
        work = sum(
            t.duration_minutes
            for t in data.tasks
            if x_values.get((t.task_id, window.window_id), 0)
        )
        span = end_values[window.window_id] - start_values[window.window_id]
        if work > 0 and span == work:
            c6_binding = True
            break
    if C6_DURATION_FEASIBILITY in by_id:
        facts.append(_entry(C6_DURATION_FEASIBILITY, c6_binding))

    # c7 binding: any activated window pinned to a §17.2 bound
    # (start == e_w, end == l_w, or span == maxdur_w).
    c7_binding = False
    for window in data.windows:
        if not y_values.get(window.window_id, 0):
            continue
        lo = int((window.earliest_start - min(w.earliest_start for w in data.windows)).total_seconds()) // 60
        hi = int((window.latest_end - min(w.earliest_start for w in data.windows)).total_seconds()) // 60
        span = end_values[window.window_id] - start_values[window.window_id]
        if (
            start_values[window.window_id] == lo
            or end_values[window.window_id] == hi
            or span == int(window.max_duration_minutes)
        ):
            c7_binding = True
            break
    if C7_WINDOW_BOUNDS in by_id:
        facts.append(_entry(C7_WINDOW_BOUNDS, c7_binding))

    for cid in (C8_PRECEDENCE, C9_DEADLINE):
        if cid in by_id:
            facts.append(_entry(cid, False))

    for cid in by_id:
        if cid not in {
            C3_QUALIFICATION,
            C4_CREW_CAPACITY,
            C6_DURATION_FEASIBILITY,
            C7_WINDOW_BOUNDS,
            C8_PRECEDENCE,
            C9_DEADLINE,
        }:
            facts.append(_entry(cid, False))
    return facts


__all__ = [
    "CpSatPlanner",
    "PlannerError",
    "STATUS_OPTIMAL",
    "STATUS_FEASIBLE",
    "STATUS_INFEASIBLE",
    "STATUS_TIMEOUT_NO_PLAN",
]
