"""Typed protocols for async scheduling components."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class Scheduler(Protocol):
    """Represents an async scheduler implementation."""

    async def start(self) -> None:
        """Start scheduler processing."""

    async def shutdown(self) -> None:
        """Gracefully stop scheduler processing."""
