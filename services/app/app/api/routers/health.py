"""Healthcheck endpoints for service liveness."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="Service health status")
async def healthcheck() -> dict[str, str]:
    """Return a simple health response."""
    return {"status": "ok"}
