from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from app.domain.engine.optimization_models import OptimizationResult, ObjectiveBreakdown, OptimizationStatus
from app.domain.models.planning import Block, CandidateBlockWindow
from app.domain.models.maintenance import MaintenanceTask
from app.domain.models.operations import OperationalWindow, TrainPath
from app.domain.engine.priority_models import PriorityResult
from app.domain.engine.models import ConstraintSeverity
from app.domain.enums import BlockStatus

SOLVER_NAME = "DeterministicBaselineOptimizer"
SOLVER_VERSION = "1.0.0"

class OptimizationConfiguration:
    def __init__(self):
        self.priority_weight = 1.0
        self.task_completion_weight = 10.0
        self.window_utilization_weight = 0.5
        self.train_impact_penalty = 5.0
        self.operational_impact_penalty = 2.0
        self.soft_constraint_penalty = 1.0

class DeterministicBaselineOptimizer:
    def __init__(self, config: Optional[OptimizationConfiguration] = None):
        self.config = config or OptimizationConfiguration()

    def _intervals_overlap(self, i1, i2) -> bool:
        return i1.start < i2.end and i2.start < i1.end

    def optimize(
        self,
        tasks: List[MaintenanceTask],
        windows: List[OperationalWindow],
        paths: List[TrainPath],
        priorities: Dict[str, PriorityResult],
        candidates_by_task: Dict[str, List[CandidateBlockWindow]],
        plan_id: Optional[str] = None,
        data_state: str = "MOCKED"
    ) -> OptimizationResult:
        
        selected_blocks = []
        unselected_tasks = []
        
        # We will sort tasks by their priority score descending
        sorted_tasks = sorted(tasks, key=lambda t: priorities[t.task_id].score if t.task_id in priorities else 0.0, reverse=True)
        
        # Keep track of assigned time intervals per section
        assigned_intervals_by_section: Dict[str, List[CandidateBlockWindow]] = {}
        
        priority_value = 0.0
        tasks_completed = 0.0
        window_utilization = 0.0
        train_impact_cost = 0.0
        operational_impact_cost = 0.0
        soft_violations_count = 0
        
        explanation_lines = []
        
        for task in sorted_tasks:
            candidates = candidates_by_task.get(task.task_id, [])
            best_candidate = None
            best_obj_delta = -999999.0
            
            # Evaluate all feasible candidates for this task
            for cand in candidates:
                # C5: Check hard constraints
                has_hard_violation = any(
                    isinstance(v, dict) and v.get("severity") == ConstraintSeverity.HARD.value
                    for v in cand.violations
                )
                if has_hard_violation:
                    continue
                    
                # C4: Check overlaps with already selected blocks in the same section
                sec_id = task.section_id
                overlaps = False
                for assigned_cand in assigned_intervals_by_section.get(sec_id, []):
                    if self._intervals_overlap(cand.interval, assigned_cand.interval):
                        overlaps = True
                        break
                if overlaps:
                    continue
                
                # Calculate objective delta if we pick this candidate
                cand_priority = priorities[task.task_id].score if task.task_id in priorities else 0.0
                cand_utilization = cand.suitability_score # simplistic mapping
                
                soft_viols = sum(
                    1 for v in cand.violations 
                    if isinstance(v, dict) and v.get("severity") == ConstraintSeverity.SOFT.value
                )
                
                # Assume train impact derived from soft violations or pre-calculated
                impact = soft_viols * self.config.soft_constraint_penalty
                
                obj_delta = (
                    cand_priority * self.config.priority_weight +
                    1.0 * self.config.task_completion_weight +
                    cand_utilization * self.config.window_utilization_weight -
                    impact
                )
                
                if obj_delta > best_obj_delta:
                    best_obj_delta = obj_delta
                    best_candidate = cand
            
            if best_candidate:
                # Select this candidate
                sec_id = task.section_id
                if sec_id not in assigned_intervals_by_section:
                    assigned_intervals_by_section[sec_id] = []
                assigned_intervals_by_section[sec_id].append(best_candidate)
                
                block_id = f"BLK-{uuid.uuid4().hex[:6].upper()}"
                b = Block(
                    block_id=block_id,
                    section_id=task.section_id,
                    interval=best_candidate.interval,
                    status=BlockStatus.DRAFT,
                    tasks=[task.task_id],
                    required_power_off=task.requires_power_block,
                    is_integrated=False
                )
                selected_blocks.append(b)
                
                priority_value += priorities[task.task_id].score if task.task_id in priorities else 0.0
                tasks_completed += 1.0
                window_utilization += best_candidate.suitability_score
                
                explanation_lines.append(
                    f"Selected {task.task_id} because: priority score = {priorities[task.task_id].score if task.task_id in priorities else 0.0:.1f}, "
                    f"no hard conflicts, utilization = {best_candidate.suitability_score:.1f}."
                )
            else:
                unselected_tasks.append(task.task_id)
                explanation_lines.append(
                    f"{task.task_id} was not selected because: no feasible block window without hard conflicts or overlaps."
                )
                
        # Total score
        total_score = (
            priority_value * self.config.priority_weight +
            tasks_completed * self.config.task_completion_weight +
            window_utilization * self.config.window_utilization_weight -
            train_impact_cost -
            operational_impact_cost
        )
        
        breakdown = ObjectiveBreakdown(
            priority_value=priority_value * self.config.priority_weight,
            tasks_completed=tasks_completed * self.config.task_completion_weight,
            window_utilization=window_utilization * self.config.window_utilization_weight,
            train_impact_cost=train_impact_cost,
            operational_impact_cost=operational_impact_cost,
            unused_window_cost=0.0,
            total_score=total_score
        )
        
        status = OptimizationStatus(
            is_optimal=True, 
            status_code="OPTIMAL" if unselected_tasks == [] else "FEASIBLE"
        )
        
        return OptimizationResult(
            plan_id=plan_id or f"PLAN-{uuid.uuid4().hex[:6].upper()}",
            selected_blocks=selected_blocks,
            unselected_tasks=unselected_tasks,
            objective_score=total_score,
            objective_breakdown=breakdown,
            feasibility_summary={"total_tasks": len(tasks), "selected": len(selected_blocks)},
            optimization_status=status,
            solver_name=SOLVER_NAME,
            solver_version=SOLVER_VERSION,
            generated_at=datetime.now(timezone.utc),
            data_state=data_state,
            explanation="\n".join(explanation_lines)
        )