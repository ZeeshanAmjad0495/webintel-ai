"""Typed protocols for async database interactions."""

from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable


@runtime_checkable
class AsyncSessionFactory(Protocol):
    """Protocol for creating async database sessions."""

    def __call__(self) -> AsyncIterator[object]:
        """Create an async iterator/session context for DB operations."""


@runtime_checkable
class UnitOfWork(Protocol):
    """Protocol describing a transactional unit of work."""

    async def __aenter__(self) -> "UnitOfWork":
        """Open transactional scope."""

    async def __aexit__(self, exc_type: object, exc: BaseException | None, tb: object) -> None:
        """Close transactional scope with commit/rollback behavior."""
