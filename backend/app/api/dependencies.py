from app.infrastructure.in_memory_maintenance_repository import InMemoryMaintenanceTaskRepository
from app.infrastructure.in_memory_plan_repository import InMemoryPlanRepository
from app.application.services.maintenance_service import MaintenanceService
from app.application.services.planning_service import PlanningService

_maintenance_repo = InMemoryMaintenanceTaskRepository()
_plan_repo = InMemoryPlanRepository()

def get_maintenance_service() -> MaintenanceService:
    return MaintenanceService(_maintenance_repo)

def get_planning_service() -> PlanningService:
    return PlanningService(_plan_repo)
