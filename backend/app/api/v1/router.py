from fastapi import APIRouter
from app.api.v1.endpoints import system, maintenance, planning

api_router = APIRouter()
api_router.include_router(system.router, tags=["system"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["maintenance"])
api_router.include_router(planning.router, tags=["planning"])
