"""Typed protocols for monitoring services."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class Monitor(Protocol):
    """Represents an async monitor workflow."""

    async def poll(self) -> None:
        """Execute one non-blocking polling cycle."""
