"""Collection of API routers for modular registration."""

from fastapi import APIRouter

from .health import router as health_router
from .jobs import router as jobs_router
from .metrics import router as metrics_router
from .monitors import router as monitors_router
from .tasks import router as tasks_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(tasks_router)
api_router.include_router(jobs_router)
api_router.include_router(monitors_router)

__all__ = ["api_router", "metrics_router"]
