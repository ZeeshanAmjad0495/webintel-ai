"""Dependency injection providers for API handlers."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from app.analysis.interfaces import Analyzer


@asynccontextmanager
async def get_db_session() -> AsyncIterator[object]:
    """Yield an async database session placeholder.

    Replace this implementation with your concrete async session factory
    (e.g., SQLAlchemy AsyncSession) once infrastructure is wired.
    """
    session: object | None = None
    try:
        yield session
    finally:
        # Keep cleanup async-ready for real DB integrations.
        session = None


async def get_analysis_service() -> Analyzer:
    """Return the analysis service implementation for request handlers.

    Raises:
        NotImplementedError: Until a concrete analyzer is registered.
    """
    raise NotImplementedError("No analyzer has been configured yet.")
