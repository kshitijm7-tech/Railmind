from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from app.domain.models.planning import Block, PlanMetrics
from app.domain.engine.priority_models import PriorityResult

class OptimizationStatus(BaseModel):
    is_optimal: bool
    status_code: str # e.g., "OPTIMAL", "FEASIBLE", "INFEASIBLE", "TIMELIMIT"

class ObjectiveBreakdown(BaseModel):
    priority_value: float
    tasks_completed: float
    window_utilization: float
    train_impact_cost: float
    operational_impact_cost: float
    unused_window_cost: float
    total_score: float

class OptimizationResult(BaseModel):
    plan_id: str
    selected_blocks: List[Block]
    unselected_tasks: List[str]
    objective_score: float
    objective_breakdown: ObjectiveBreakdown
    feasibility_summary: Dict[str, Any]
    optimization_status: OptimizationStatus
    solver_name: str
    solver_version: str
    generated_at: datetime
    data_state: str
    explanation: str