from fastapi import APIRouter
from app.api.v1.endpoints import system, maintenance, planning, infrastructure, operations, decision, engine

api_router = APIRouter()
api_router.include_router(system.router, tags=["system"])
api_router.include_router(infrastructure.router, tags=["infrastructure"])
api_router.include_router(operations.router, tags=["operations"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["maintenance"])
api_router.include_router(planning.router, tags=["planning"])
api_router.include_router(decision.router, tags=["decision"])
api_router.include_router(engine.router, prefix="/engine", tags=["engine"])
