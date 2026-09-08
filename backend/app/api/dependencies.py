from app.infrastructure.in_memory_maintenance_repository import InMemoryMaintenanceRepository
from app.infrastructure.in_memory_plan_repository import InMemoryPlanRepository
from app.infrastructure.in_memory_infrastructure_repository import InMemoryInfrastructureRepository
from app.infrastructure.in_memory_operations_repository import InMemoryOperationsRepository
from app.application.services.maintenance_service import MaintenanceService
from app.application.services.planning_service import PlanningService
from app.application.services.infrastructure_service import InfrastructureService
from app.application.services.operations_service import OperationsService

_infrastructure_repo = InMemoryInfrastructureRepository()
_operations_repo = InMemoryOperationsRepository()
_maintenance_repo = InMemoryMaintenanceRepository()
_plan_repo = InMemoryPlanRepository()

def get_infrastructure_service() -> InfrastructureService:
    return InfrastructureService(_infrastructure_repo)

def get_operations_service() -> OperationsService:
    return OperationsService(_operations_repo)

def get_maintenance_service() -> MaintenanceService:
    return MaintenanceService(_maintenance_repo)

def get_planning_service() -> PlanningService:
    return PlanningService(_plan_repo)
