"""§17.4 CP-SAT model builder (E09).

Builds the CP-SAT model for one ``PlannerInput`` exactly as blueprint
§17.1–§17.4 specifies. Nothing here ranks, scores or evaluates the §17.5
objective — E03 owns those semantics; this module enforces the hard
constraints and exposes the solved variables to the solution extractor.

Determinism (blueprint §26, TRD §67): solves are pinned to
``num_workers=1`` and an explicit ``random_seed``; ``max_time_in_seconds``
comes from ``PlannerConfig`` (TRD §65). Same input + config → same plan.

Time encoding: windows are solved on integer minutes from the horizon
zero-point (the minimum ``earliest_start`` across windows), so every §17.4
constraint maps to exact integer arithmetic; the extractor converts offsets
back to datetimes.

Constraint coverage (§17.4 Tier-1): c1 assignment, c2 window activation,
c3 crew qualification, c4 crew capacity (per window, per department; the
§17.4 c6 note makes parallel-crew bundling a Tier 2 refinement, so
sequential execution within a window makes a per-window capacity check
exact), c5 section exclusivity (no-overlap per section), c6 duration
feasibility (span ≥ Σ assigned work), c7 window bounds incl. maxdur_w,
c8 task precedence, c9 deadlines.
"""

from datetime import timedelta
from typing import Dict, List, Tuple

from ortools.sat.python import cp_model

from engine.planner.inputs import PlannerInput, TaskInput, WindowInput

#: §17.4 constraint identities used in the trace.
C1_ASSIGNMENT = "c1_assignment"
C2_ACTIVATION = "c2_window_activation"
C3_QUALIFICATION = "c3_crew_qualification"
C4_CREW_CAPACITY = "c4_crew_capacity"
C5_SECTION_EXCLUSIVITY = "c5_section_exclusivity"
C6_DURATION_FEASIBILITY = "c6_duration_feasibility"
C7_WINDOW_BOUNDS = "c7_window_bounds"
C8_PRECEDENCE = "c8_task_precedence"
C9_DEADLINE = "c9_deadline"


def minutes_between(earlier, later, *, allow_negative: bool = False) -> int:
    """Integer minutes from ``earlier`` to ``later``.

    Zero is legitimate (the first window starts at the horizon zero-point);
    negative deltas are rejected by default (inverted bounds). c9 deadlines
    pass ``allow_negative``: a deadline earlier than the horizon zero-point
    is not an inverted bound — it makes every c9-feasible assignment
    impossible, which the §17.3 slack converts into a forced unschedule.
    """
    seconds = int((later - earlier).total_seconds())
    if seconds < 0 and not allow_negative:
        raise ValueError(
            f"inverted time bounds; got {earlier!r} -> {later!r}"
        )
    return seconds // 60


class PlannerModel:
    """Variables + CP-SAT model + constraint-trace facts for one solve."""

    def __init__(self, data: PlannerInput):
        self.data = data
        self.model = cp_model.CpModel()
        self.x: Dict[Tuple[str, str], object] = {}
        self.y: Dict[str, object] = {}
        self.starts: Dict[str, object] = {}
        self.ends: Dict[str, object] = {}
        self.spans: Dict[str, object] = {}
        self.unscheduled: Dict[str, object] = {}
        self.traces: List[dict] = []

        self._horizon_zero = min(
            (w.earliest_start for w in data.windows), default=None
        )
        self._build()

    # --- offsets -----------------------------------------------------------

    def _offset(self, when) -> int:
        assert self._horizon_zero is not None
        return minutes_between(self._horizon_zero, when, allow_negative=True)

    # --- construction ------------------------------------------------------

    def _build(self) -> None:
        model = self.model

        if not self.data.windows:
            # Degenerate instance: c1's slack forces every task unscheduled.
            for task in self.data.tasks:
                u = model.NewBoolVar(f"unscheduled[{task.task_id}]")
                model.Add(u == 1)
                self.unscheduled[task.task_id] = u
            self.traces.append(
                {
                    "constraint_id": C1_ASSIGNMENT,
                    "description": "no candidate windows supplied",
                    "role": "active",
                }
            )
            return

        # §17.3 variables.
        for window in self.data.windows:
            lo = self._offset(window.earliest_start)
            hi = self._offset(window.latest_end)
            start = model.NewIntVar(lo, hi, f"start[{window.window_id}]")
            end = model.NewIntVar(lo, hi, f"end[{window.window_id}]")
            span = model.NewIntVar(0, hi - lo, f"span[{window.window_id}]")
            model.Add(start + span == end)
            # IntervalVar for c5; zero-length when the window is not
            # activated, so inactive windows never block the section.
            model.NewIntervalVar(start, span, end, f"block[{window.window_id}]")
            y = model.NewBoolVar(f"y[{window.window_id}]")
            model.Add(span == 0).OnlyEnforceIf(y.Not())
            self.starts[window.window_id] = start
            self.ends[window.window_id] = end
            self.spans[window.window_id] = span
            self.y[window.window_id] = y

        self._c1_c2_assignment_and_activation()
        self._c3_qualification()
        self._c6_duration_feasibility()
        self._c7_window_bounds()
        self._c5_section_exclusivity()
        self._c4_crew_capacity()
        self._c8_precedence()
        self._c9_deadlines()

    def _c1_c2_assignment_and_activation(self) -> None:
        model = self.model
        for task in self.data.tasks:
            u = model.NewBoolVar(f"unscheduled[{task.task_id}]")
            self.unscheduled[task.task_id] = u
            terms = [u]
            for window in self.data.windows:
                x = model.NewBoolVar(f"x[{task.task_id},{window.window_id}]")
                self.x[(task.task_id, window.window_id)] = x
                terms.append(x)
                # c2: x[t,w] ≤ y[w]
                model.AddImplication(x, self.y[window.window_id])
            # c1: Σ_w x[t,w] + unscheduled[t] = 1
            model.AddExactlyOne(terms)
        self.traces.append(
            {
                "constraint_id": C1_ASSIGNMENT,
                "description": "Σ_w x[t,w] + unscheduled[t] = 1 per task",
                "role": "active",
            }
        )
        self.traces.append(
            {
                "constraint_id": C2_ACTIVATION,
                "description": "x[t,w] ≤ y[w] for all t, w",
                "role": "active",
            }
        )

    def _c3_qualification(self) -> None:
        model = self.model
        for task in self.data.tasks:
            for window in self.data.windows:
                if task.department not in window.qualified_departments:
                    model.Add(self.x[(task.task_id, window.window_id)] == 0)
        self.traces.append(
            {
                "constraint_id": C3_QUALIFICATION,
                "description": "x[t,w] = 0 when dept(t) lacks qualified crew for w",
                "role": "active",
            }
        )

    def _c6_duration_feasibility(self) -> None:
        model = self.model
        for window in self.data.windows:
            workload = [
                int(task.duration_minutes) * self.x[(task.task_id, window.window_id)]
                for task in self.data.tasks
            ]
            model.Add(sum(workload) <= self.spans[window.window_id]).OnlyEnforceIf(
                self.y[window.window_id]
            )
        self.traces.append(
            {
                "constraint_id": C6_DURATION_FEASIBILITY,
                "description": "end[w] - start[w] ≥ Σ_t dur_t · x[t,w]",
                "role": "active",
            }
        )

    def _c7_window_bounds(self) -> None:
        model = self.model
        for window in self.data.windows:
            # maxdur_w: end - start ≤ maxdur_w (holds trivially when inactive).
            model.Add(
                self.spans[window.window_id] <= int(window.max_duration_minutes)
            )
        self.traces.append(
            {
                "constraint_id": C7_WINDOW_BOUNDS,
                "description": "e_w ≤ start[w], end[w] ≤ l_w, span ≤ maxdur_w "
                "(bounds via variable domains)",
                "role": "active",
            }
        )

    def _c5_section_exclusivity(self) -> None:
        model = self.model
        by_section: Dict[str, List[str]] = {}
        for window in self.data.windows:
            by_section.setdefault(window.section_id, []).append(window.window_id)
        for section_id in sorted(by_section):
            window_ids = by_section[section_id]
            if len(window_ids) > 1:
                model.AddNoOverlap(
                    [
                        model.NewIntervalVar(
                            self.starts[w],
                            self.spans[w],
                            self.ends[w],
                            f"nooverlap[{section_id},{w}]",
                        )
                        for w in window_ids
                    ]
                )
        self.traces.append(
            {
                "constraint_id": C5_SECTION_EXCLUSIVITY,
                "description": "windows on the same section never overlap",
                "role": "active",
            }
        )

    def _c4_crew_capacity(self) -> None:
        model = self.model
        pools: Dict[str, Dict[str, int]] = {}
        for pool in self.data.crew_pools:
            pools.setdefault(pool.department, {})[pool.shift_id] = pool.available_crew
        if not pools:
            return
        departments = {task.department for task in self.data.tasks}
        for department in sorted(departments):
            shift_counts = pools.get(department)
            if not shift_counts:
                continue
            limit = max(shift_counts.values())
            for window in self.data.windows:
                crew_terms = [
                    task.crew_size * self.x[(task.task_id, window.window_id)]
                    for task in self.data.tasks
                    if task.department == department
                ]
                if crew_terms:
                    model.Add(sum(crew_terms) <= limit).OnlyEnforceIf(
                        self.y[window.window_id]
                    )
        self.traces.append(
            {
                "constraint_id": C4_CREW_CAPACITY,
                "description": "Σ_t crew_t · x[t,w] ≤ avail_d per window/dept",
                "role": "active",
            }
        )

    def _c8_precedence(self) -> None:
        model = self.model
        for before_id, after_id in self.data.precedence:
            for w1 in self.data.windows:
                x_before = self.x[(before_id, w1.window_id)]
                for w2 in self.data.windows:
                    x_after = self.x[(after_id, w2.window_id)]
                    # c8: when before∈w1 and after∈w2 (both activated),
                    # end[w1] ≤ start[w2]. OnlyEnforceIf's literal list is a
                    # conjunction — no auxiliary reification variable needed.
                    # Same-window pairs (w1 == w2) are therefore forbidden
                    # (end[w] ≤ start[w] is unsatisfiable): the literal
                    # §17.4 c8 text ("the window containing t' must start no
                    # earlier than the window containing t ends") admits no
                    # intra-window sequencing at Tier 1 — documented.
                    model.Add(
                        self.ends[w1.window_id] <= self.starts[w2.window_id]
                    ).OnlyEnforceIf(
                        [
                            x_before,
                            x_after,
                            self.y[w1.window_id],
                            self.y[w2.window_id],
                        ]
                    )
        if self.data.precedence:
            self.traces.append(
                {
                    "constraint_id": C8_PRECEDENCE,
                    "description": "end[w_before] ≤ start[w_after] when dep(t,t')",
                    "role": "active",
                }
            )

    def _c9_deadlines(self) -> None:
        model = self.model
        enforced = False
        for task in self.data.tasks:
            if task.latest_finish is None:
                continue
            deadline_offset = self._offset(task.latest_finish)
            for window in self.data.windows:
                model.Add(
                    self.ends[window.window_id] <= deadline_offset
                ).OnlyEnforceIf(self.x[(task.task_id, window.window_id)])
            enforced = True
        if enforced:
            self.traces.append(
                {
                    "constraint_id": C9_DEADLINE,
                    "description": "end[w] ≤ latest_finish for windows holding t",
                    "role": "active",
                }
            )


__all__ = [
    "PlannerModel",
    "minutes_between",
    "C1_ASSIGNMENT",
    "C2_ACTIVATION",
    "C3_QUALIFICATION",
    "C4_CREW_CAPACITY",
    "C5_SECTION_EXCLUSIVITY",
    "C6_DURATION_FEASIBILITY",
    "C7_WINDOW_BOUNDS",
    "C8_PRECEDENCE",
    "C9_DEADLINE",
]
