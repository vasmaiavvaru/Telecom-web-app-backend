from fastapi import APIRouter

from app.api.v1 import plans

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(plans.router, prefix="/plans", tags=["plans"])
