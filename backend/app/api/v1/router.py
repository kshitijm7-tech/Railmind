from fastapi import APIRouter
from app.api.v1.endpoints import system, maintenance, planning, infrastructure, operations, decision, priority, simulation, ingestion, forecasting, risk, intelligence, recovery

api_router = APIRouter()
api_router.include_router(system.router, tags=["system"])
api_router.include_router(infrastructure.router, tags=["infrastructure"])
api_router.include_router(operations.router, tags=["operations"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["maintenance"])
api_router.include_router(planning.router, tags=["planning"])
api_router.include_router(decision.router, tags=["decision"])
api_router.include_router(priority.router, tags=["priority"])
api_router.include_router(ingestion.router, prefix="/ingestion", tags=["Integration"])
api_router.include_router(forecasting.router, prefix="/forecasting", tags=["forecasting"])
api_router.include_router(risk.router, prefix="/risk", tags=["risk"])
api_router.include_router(simulation.router, prefix="/simulations", tags=["simulation"])
api_router.include_router(intelligence.router, prefix="/intelligence", tags=["intelligence"])
api_router.include_router(recovery.router, prefix="/recovery", tags=["recovery"])