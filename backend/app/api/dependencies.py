from app.infrastructure.in_memory_maintenance_repository import InMemoryMaintenanceRepository
from app.infrastructure.in_memory_plan_repository import InMemoryPlanRepository
from app.infrastructure.database.repositories import PostgresPlanRepository
from app.infrastructure.database.session import get_db
from app.core.config import settings
from app.infrastructure.in_memory_infrastructure_repository import InMemoryInfrastructureRepository
from app.infrastructure.in_memory_operations_repository import InMemoryOperationsRepository
from app.infrastructure.in_memory_decision_repository import InMemoryDecisionRepository, InMemoryAuditRepository
from app.application.services.maintenance_service import MaintenanceService
from app.application.services.planning_service import PlanningService
from app.application.services.infrastructure_service import InfrastructureService
from app.application.services.operations_service import OperationsService
from app.application.services.decision_service import DecisionService
from app.engine_adapter.service import EngineIntegrationService

_infrastructure_repo = InMemoryInfrastructureRepository()
_operations_repo = InMemoryOperationsRepository()
_maintenance_repo = InMemoryMaintenanceRepository()
if settings.DATABASE_ENABLED:
    _plan_repo = PostgresPlanRepository(get_db)
else:
    _plan_repo = InMemoryPlanRepository()
_decision_repo = InMemoryDecisionRepository()
_audit_repo = InMemoryAuditRepository()

def get_infrastructure_service() -> InfrastructureService:
    return InfrastructureService(_infrastructure_repo)

def get_operations_service() -> OperationsService:
    return OperationsService(_operations_repo)

def get_maintenance_service() -> MaintenanceService:
    return MaintenanceService(_maintenance_repo)

def get_planning_service() -> PlanningService:
    return PlanningService(_plan_repo, _infrastructure_repo, _maintenance_repo, _operations_repo, get_engine_integration_service())

def get_decision_service() -> DecisionService:
    return DecisionService(_decision_repo, _audit_repo, _plan_repo)

def get_engine_integration_service() -> EngineIntegrationService:
    """E07: the engine facade (stateless; the engine is the domain authority)."""
    return EngineIntegrationService()

from app.application.services.simulation_service import SimulationService

_simulation_service = SimulationService(_plan_repo, _operations_repo, _maintenance_repo)

def get_simulation_service() -> SimulationService:
    return _simulation_service
