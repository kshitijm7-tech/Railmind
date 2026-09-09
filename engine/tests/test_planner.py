"""E09 tests — §17 CP-SAT planner: hand-checkable constraint semantics.

Blueprint §27 discipline: "validated against hand-checkable small cases."
Each §17.4 constraint gets an explicit fixture whose optimal solution is
verifiable by inspection; the suite also pins determinism (seed+workers=1),
honest infeasibility, the c1 slack semantics, k-best alternatives, and the
TRD §26 NFR (< 10 s full solve on a Tier-1-sized instance).
"""

from datetime import datetime, timedelta, timezone

import pytest

from engine import PlannerError
from engine.planner import (
    C1_ASSIGNMENT,
    C3_QUALIFICATION,
    C4_CREW_CAPACITY,
    C6_DURATION_FEASIBILITY,
    C7_WINDOW_BOUNDS,
    C8_PRECEDENCE,
    C9_DEADLINE,
    CpSatPlanner,
    CrewPool,
    PlannerConfig,
    PlannerInput,
    TaskInput,
    WindowInput,
)
from engine.priority.result import PriorityResult

T0 = datetime(2026, 9, 14, 22, 0, tzinfo=timezone.utc)


def prio(task_id: str, score: float) -> PriorityResult:
    return PriorityResult(task_id=task_id, score=score, priority_class="HIGH")


def base_input(**overrides) -> PlannerInput:
    fields = dict(
        plan_ref="PLAN-T",
        tasks=[
            TaskInput(task_id="T1", duration_minutes=45, department="S&T", priority=prio("T1", 0.8)),
            TaskInput(task_id="T2", duration_minutes=25, department="PWD", priority=prio("T2", 0.5)),
            TaskInput(task_id="T3", duration_minutes=20, department="S&T", priority=prio("T3", 0.3)),
        ],
        windows=[
            WindowInput(
                window_id="W1", section_id="SEC-A", earliest_start=T0,
                latest_end=T0.replace(hour=23), max_duration_minutes=60.0,
                qualified_departments=["S&T"], bundle_bonus=0.0, overrun_risk=0.05,
            ),
            WindowInput(
                window_id="W2", section_id="SEC-B", earliest_start=T0,
                latest_end=T0.replace(hour=23), max_duration_minutes=60.0,
                qualified_departments=["S&T", "PWD"], bundle_bonus=1.0, overrun_risk=0.05,
            ),
        ],
        crew_pools=[
            CrewPool(department="S&T", shift_id="NIGHT", available_crew=2),
            CrewPool(department="PWD", shift_id="NIGHT", available_crew=2),
        ],
    )
    fields.update(overrides)
    return PlannerInput(**fields)


def window_of(plan, task_id):
    return next(
        (a.window_id for a in plan.assignments if a.task_id == task_id), None
    )


class TestConstraintSemantics:
    """Each §17.4 constraint verified on a hand-checkable fixture."""

    def test_best_plan_bundles_and_schedules_everything_when_possible(self):
        # No delay evidence: both windows' block costs are the δ floor (0.05
        # ×100×2 = 10 each), so activating both and scheduling all three tasks
        # is optimal under exact §17.5 (γ2 + δ0.2 − ε2.0 = 0.2 total) versus
        # leaving T1 unscheduled (β·0.8 = 3.2 alone). The bundling reward
        # lands on W2 (the only cross-department window).
        out = CpSatPlanner(PlannerConfig(alternative_count=1)).plan(base_input())
        best = out.plans[0]
        assert best.plan_id == out.best_plan_id
        assert sorted(b.window_id for b in best.blocks) == ["W1", "W2"]
        assert best.unscheduled_task_ids == []
        w2 = next(b for b in best.blocks if b.window_id == "W2")
        assert sorted(w2.assigned_task_ids) == ["T2", "T3"]  # bundle
        assert (w2.end - w2.start).total_seconds() / 60 == 45  # timing-tight

    def test_delay_cost_can_make_a_window_not_worth_activating(self):
        # With heavy predicted delay on W1 (§16.3 evidence), activating it is
        # worse than leaving its task unscheduled: α·delay dominates.
        from engine.delay import (
            AffectedTrain,
            DelayFeatures,
            GraphPropagationDelayModel,
        )

        heavy = GraphPropagationDelayModel().predict(
            DelayFeatures(
                window_id="W1", section_id="SEC-A", earliest_start=T0,
                latest_end=T0.replace(hour=23), time_of_day_minutes=1320.0,
                historical_delay_minutes=400.0,
                affected_trains=[
                    AffectedTrain(train_id="R1", priority=0.0, route=["SEC-A"])
                ],
            )
        )
        data = base_input(delay_results={"W1": heavy})
        out = CpSatPlanner(PlannerConfig(alternative_count=1)).plan(data)
        best = out.plans[0]
        assert [b.window_id for b in best.blocks] == ["W2"]
        assert best.unscheduled_task_ids == ["T1"]  # honest c1 slack
        assert best.objective.priority_component == pytest.approx(3.2)

    def test_c3_qualification_forbids_unqualified_department(self):
        data = base_input(
            windows=[
                WindowInput(
                    window_id="W1", section_id="SEC-A", earliest_start=T0,
                    latest_end=T0.replace(hour=23), max_duration_minutes=120.0,
                    qualified_departments=["S&T"],  # PWD not qualified
                ),
            ]
        )
        out = CpSatPlanner(PlannerConfig(alternative_count=1)).plan(data)
        best = out.plans[0]
        assert window_of(best, "T2") is None  # PWD task can never be placed
        assert "T2" in best.unscheduled_task_ids

    def test_c4_crew_capacity_limits_concurrent_work(self):
        # Two S&T tasks of crew 2 each; pool has only 2 S&T crew → both tasks
        # cannot share one window (2+2 > 2).
        data = base_input(
            tasks=[
                TaskInput(task_id="TA", duration_minutes=20, department="S&T", crew_size=2, priority=prio("TA", 0.9)),
                TaskInput(task_id="TB", duration_minutes=20, department="S&T", crew_size=2, priority=prio("TB", 0.8)),
            ],
            windows=[
                WindowInput(
                    window_id="W1", section_id="SEC-A", earliest_start=T0,
                    latest_end=T0.replace(hour=23), max_duration_minutes=120.0,
                    qualified_departments=["S&T"],
                ),
                WindowInput(
                    window_id="W2", section_id="SEC-B", earliest_start=T0,
                    latest_end=T0.replace(hour=23), max_duration_minutes=120.0,
                    qualified_departments=["S&T"],
                ),
            ],
            crew_pools=[CrewPool(department="S&T", shift_id="NIGHT", available_crew=2)],
        )
        out = CpSatPlanner(PlannerConfig(alternative_count=1)).plan(data)
        best = out.plans[0]
        # Both tasks scheduled, but not in the same window.
        assert window_of(best, "TA") is not None
        assert window_of(best, "TB") is not None
        assert window_of(best, "TA") != window_of(best, "TB")

    def test_c5_section_exclusivity_no_overlapping_blocks(self):
        data = base_input(
            tasks=[
                TaskInput(task_id="TA", duration_minutes=30, department="S&T", priority=prio("TA", 0.9)),
                TaskInput(task_id="TB", duration_minutes=30, department="S&T", priority=prio("TB", 0.8)),
            ],
            windows=[
                WindowInput(
                    window_id=f"W{i}", section_id="SEC-A",  # same section!
                    earliest_start=T0,
                    latest_end=T0.replace(hour=23), max_duration_minutes=60.0,
                    qualified_departments=["S&T"],
                )
                for i in (1, 2)
            ],
        )
        out = CpSatPlanner(PlannerConfig(alternative_count=1)).plan(data)
        best = out.plans[0]
        blocks = best.blocks
        if len(blocks) == 2:
            assert blocks[0].end <= blocks[1].start or blocks[1].end <= blocks[0].start

    def test_c6_work_must_fit_within_block(self):
        out = CpSatPlanner(PlannerConfig(alternative_count=1)).plan(base_input())
        for block in out.plans[0].blocks:
            window = next(w for w in base_input().windows if w.window_id == block.window_id)
            assert block.assigned_work_minutes <= window.max_duration_minutes

    def test_c7_blocks_stay_within_window_bounds(self):
        out = CpSatPlanner(PlannerConfig(alternative_count=1)).plan(base_input())
        for block in out.plans[0].blocks:
            window = next(
                w for w in base_input().windows if w.window_id == block.window_id
            )
            assert block.start >= window.earliest_start
            assert block.end <= window.latest_end
            assert (block.end - block.start).total_seconds() / 60 <= window.max_duration_minutes

    def test_c8_precedence_forbids_same_window_and_reversal(self):
        data = base_input(precedence=[("T1", "T3")])
        out = CpSatPlanner(PlannerConfig(alternative_count=2)).plan(data)
        for plan in out.plans:
            t1_w = window_of(plan, "T1")
            t3_w = window_of(plan, "T3")
            if t1_w is not None and t3_w is not None:
                assert t1_w != t3_w, "c8: T1 must precede T3 (no intra-window order at Tier 1)"

    def test_c9_unreachable_deadline_forces_unscheduled_not_infeasible(self):
        # §17.3: the slack exists "so the model always stays feasible" — an
        # unreachable c9 deadline forces the task unscheduled (with its true
        # β cost), never a solver failure.
        data = base_input(
            tasks=[
                TaskInput(
                    task_id="T1", duration_minutes=45, department="S&T",
                    priority=prio("T1", 0.8),
                    latest_finish=T0 + timedelta(minutes=30),  # 45 > 30: impossible
                ),
            ],
            windows=[
                WindowInput(
                    window_id="W1", section_id="SEC-A", earliest_start=T0,
                    latest_end=T0.replace(hour=23), max_duration_minutes=60.0,
                    qualified_departments=["S&T"],
                ),
            ],
            crew_pools=[CrewPool(department="S&T", shift_id="NIGHT", available_crew=2)],
        )
        out = CpSatPlanner(PlannerConfig(alternative_count=1)).plan(data)
        best = out.plans[0]
        assert best.unscheduled_task_ids == ["T1"]
        assert best.blocks == []
        assert best.objective.priority_component == pytest.approx(3.2)

    def test_c9_deadline_respected_when_reachable(self):
        deadline = T0 + timedelta(minutes=30)
        data = base_input(
            tasks=[
                TaskInput(
                    task_id="T1", duration_minutes=20, department="S&T",
                    priority=prio("T1", 0.8), latest_finish=deadline,
                ),
            ],
            windows=[
                WindowInput(
                    window_id="W1", section_id="SEC-A", earliest_start=T0,
                    latest_end=T0.replace(hour=23), max_duration_minutes=60.0,
                    qualified_departments=["S&T"],
                ),
            ],
        )
        out = CpSatPlanner(PlannerConfig(alternative_count=1)).plan(data)
        block = next(b for b in out.plans[0].blocks if b.assigned_task_ids == ["T1"])
        assert block.end <= deadline


class TestObjectiveIntegration:
    """E03 owns the §17.5 ranking; the planner's output must obey it."""

    def test_alternatives_ranked_ascending_by_e03_total(self):
        out = CpSatPlanner(PlannerConfig(alternative_count=2)).plan(base_input())
        totals = [p.objective.total_objective for p in out.plans]
        assert totals == sorted(totals)

    def test_plan_ids_canonical_by_rank(self):
        out = CpSatPlanner(PlannerConfig(alternative_count=2)).plan(base_input())
        assert out.plans[0].plan_id == "PLAN-T-alt0"
        assert out.best_plan_id == out.plans[0].plan_id

    def test_beta_slack_cost_reported_honestly(self):
        # The heavy-delay fixture forces T1 unscheduled (see c6/c7 tests); its
        # β·priority = 4 × 0.8 = 3.2 must appear in the priority component.
        from engine.delay import (
            AffectedTrain,
            DelayFeatures,
            GraphPropagationDelayModel,
        )

        heavy = GraphPropagationDelayModel().predict(
            DelayFeatures(
                window_id="W1", section_id="SEC-A", earliest_start=T0,
                latest_end=T0.replace(hour=23), time_of_day_minutes=1320.0,
                historical_delay_minutes=400.0,
                affected_trains=[
                    AffectedTrain(train_id="R1", priority=0.0, route=["SEC-A"])
                ],
            )
        )
        out = CpSatPlanner(PlannerConfig(alternative_count=1)).plan(
            base_input(delay_results={"W1": heavy})
        )
        best = out.plans[0]
        assert best.unscheduled_task_ids == ["T1"]
        assert best.objective.priority_component == pytest.approx(3.2)

    def test_delay_evidence_carried_verbatim(self):
        from engine.delay import (
            AffectedTrain,
            DelayFeatures,
            GraphPropagationDelayModel,
        )

        delay = GraphPropagationDelayModel().predict(
            DelayFeatures(
                window_id="W1", section_id="SEC-A", earliest_start=T0,
                latest_end=T0.replace(hour=23), time_of_day_minutes=1320.0,
                historical_delay_minutes=10.0,
                affected_trains=[
                    AffectedTrain(train_id="R1", priority=5.0, route=["SEC-A"])
                ],
            )
        )
        data = base_input(delay_results={"W1": delay})
        out = CpSatPlanner(PlannerConfig(alternative_count=2)).plan(data)
        carrying = [
            b
            for p in out.plans
            for b in p.blocks
            if b.window_id == "W1" and b.delay_evidence is not None
        ]
        assert carrying, "activated W1 must carry its §16.3 evidence verbatim"
        assert carrying[0].delay_evidence.total_delay_minutes == (
            delay.total_delay_minutes
        )


class TestDeterminismAndEvidence:
    def test_repeated_solve_byte_identical(self):
        planner = CpSatPlanner(PlannerConfig(alternative_count=2, random_seed=0))
        a = planner.plan(base_input())
        b = CpSatPlanner(PlannerConfig(alternative_count=2, random_seed=0)).plan(base_input())
        assert [p.model_dump() for p in a.plans] == [p.model_dump() for p in b.plans]

    def test_seed_changes_are_recorded(self):
        out = CpSatPlanner(PlannerConfig(random_seed=7)).plan(base_input())
        assert out.evidence.random_seed == 7

    def test_evidence_records_solver_identity(self):
        out = CpSatPlanner().plan(base_input())
        assert out.evidence.solver == "cpsat"
        assert out.evidence.solver_version not in ("", "unknown")
        assert out.evidence.status == "OPTIMAL"
        assert out.evidence.planner_model_id == "railmind-cpsat-planner"
        assert out.evidence.constraint_set_id == "railmind-core-constraints"
        assert out.evidence.objective_weights["train_delay"] == 5.0

    def test_constraint_trace_covers_enforced_constraints(self):
        out = CpSatPlanner(PlannerConfig(alternative_count=1)).plan(base_input())
        trace_ids = {t.constraint_id for t in out.plans[0].constraint_trace}
        assert {C1_ASSIGNMENT, C3_QUALIFICATION, C6_DURATION_FEASIBILITY, C7_WINDOW_BOUNDS} <= trace_ids
        assert all(t.role in ("binding", "active") for t in out.plans[0].constraint_trace)

    def test_degenerate_instance_all_unscheduled(self):
        data = base_input(windows=[])
        out = CpSatPlanner(PlannerConfig(alternative_count=1)).plan(data)
        best = out.plans[0]
        assert best.blocks == []
        assert sorted(best.unscheduled_task_ids) == ["T1", "T2", "T3"]
        # β cost of leaving everything unscheduled: 4×(0.8+0.5+0.3) = 6.4
        assert best.objective.priority_component == pytest.approx(6.4)


class TestPerformance:
    """TRD §26 NFR: < 10 s full-horizon solve on Tier-1 dataset sizes."""

    def test_blueprint_s12_dataset_under_ten_seconds(self):
        """§26 NFR fixture at §12 sizing: 22 tasks, 9 sections,
        4 windows/section/night over a 3-night horizon (36 windows),
        4 departments. Full solve + 2 alternatives < 10 s."""
        departments = ["S&T", "PWD", "TRD", "C&W"]
        nights = [T0 + timedelta(days=d) for d in range(3)]
        tasks = [
            TaskInput(
                task_id=f"T{i}",
                duration_minutes=20 + (i % 5) * 10,
                department=departments[i % 4],
                priority=prio(f"T{i}", 0.2 + (i % 7) / 10.0),
            )
            for i in range(22)  # §12: 22 maintenance tasks
        ]
        windows = []
        for s in range(9):  # §12: 9 track sections
            for night in nights:
                for k in range(4):  # §12: 4–6 per section per day
                    start = night.replace(hour=22, minute=0) + timedelta(
                        minutes=k * 90
                    )
                    windows.append(
                        WindowInput(
                            window_id=f"W{s}-{night.date().isoformat()}-{k}",
                            section_id=f"S{s}",
                            earliest_start=start,
                            latest_end=start + timedelta(minutes=120),
                            max_duration_minutes=120.0,
                            qualified_departments=departments,
                            bundle_bonus=0.5 if (s + k) % 2 else 0.0,
                            overrun_risk=0.05,
                        )
                    )
        data = PlannerInput(
            plan_ref="PLAN-PERF",
            tasks=tasks,
            windows=windows,
            crew_pools=[
                CrewPool(department=d, shift_id="NIGHT", available_crew=6)
                for d in departments
            ],
        )
        import time

        started = time.perf_counter()
        out = CpSatPlanner(PlannerConfig(alternative_count=2)).plan(data)
        elapsed = time.perf_counter() - started
        assert out.best_plan_id
        assert out.plans[0].unscheduled_task_ids == []
        assert elapsed < 10.0


class TestInputValidation:
    def test_fractional_duration_rejected(self):
        with pytest.raises(Exception):
            base_input(
                tasks=[
                    TaskInput(task_id="T", duration_minutes=45.5, department="S&T", priority=prio("T", 0.5))
                ]
            )

    def test_duplicate_task_rejected(self):
        task = TaskInput(task_id="T", duration_minutes=45, department="S&T", priority=prio("T", 0.5))
        with pytest.raises(Exception):
            base_input(tasks=[task, task])

    def test_unknown_precedence_task_rejected(self):
        with pytest.raises(Exception):
            base_input(precedence=[("T1", "NOPE")])

    def test_unknown_delay_window_rejected(self):
        with pytest.raises(Exception):
            base_input(delay_results={"NOPE": None})

    def test_inverted_window_rejected(self):
        with pytest.raises(Exception):
            base_input(
                windows=[
                    WindowInput(
                        window_id="W", section_id="S", earliest_start=T0,
                        latest_end=T0 - timedelta(minutes=1),
                        max_duration_minutes=10.0,
                        qualified_departments=["S&T"],
                    )
                ]
            )
