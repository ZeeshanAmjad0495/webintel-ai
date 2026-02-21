"""Async SQLAlchemy engine/session helpers for FastAPI."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.settings import Settings, get_settings


def create_engine(settings: Settings | None = None) -> AsyncEngine:
    """Create and return the application's async SQLAlchemy engine."""

    cfg = settings or get_settings()
    return create_async_engine(cfg.database_url, future=True, pool_pre_ping=True)


engine: AsyncEngine = create_engine()
AsyncSessionFactory = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding an async database session."""

    async with AsyncSessionFactory() as session:
        yield session


def db_session_dependency(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncSession:
    """Reusable dependency alias for endpoint signatures."""

    return session
