"""Typed protocols for analysis services."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class Analyzer(Protocol):
    """Represents an async analyzer service."""

    async def analyze(self, payload: dict[str, object]) -> dict[str, object]:
        """Analyze payload data and return normalized results."""
