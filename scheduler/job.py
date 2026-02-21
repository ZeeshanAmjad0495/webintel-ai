from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Awaitable, Callable, Optional, Protocol


class JobState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    RETRYING = "retrying"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobMetricsHook(Protocol):
    """Optional lifecycle callback interface for job metrics."""

    def on_job_started(self, job: "Job") -> None: ...

    def on_job_retry(self, job: "Job", exc: Exception, retry_in: float) -> None: ...

    def on_job_succeeded(self, job: "Job", duration_s: float) -> None: ...

    def on_job_failed(self, job: "Job", exc: Exception, duration_s: float) -> None: ...

    def on_job_cancelled(self, job: "Job") -> None: ...


@dataclass(slots=True)
class Job:
    """Represents an executable async unit with lifecycle and retry behavior."""

    id: str
    handler: Callable[[], Awaitable[Any]]
    max_retries: int = 0
    retry_backoff_s: float = 0.0
    metrics_hook: Optional[JobMetricsHook] = None

    state: JobState = field(default=JobState.PENDING, init=False)
    attempts: int = field(default=0, init=False)
    last_error: Optional[str] = field(default=None, init=False)
    last_started_at: Optional[datetime] = field(default=None, init=False)
    last_finished_at: Optional[datetime] = field(default=None, init=False)

    async def execute(self) -> Any:
        started_monotonic = asyncio.get_running_loop().time()
        self.state = JobState.RUNNING
        self.attempts += 1
        self.last_started_at = datetime.now(timezone.utc)

        if self.metrics_hook:
            self.metrics_hook.on_job_started(self)

        try:
            result = await self.handler()
        except asyncio.CancelledError:
            self.state = JobState.CANCELLED
            self.last_finished_at = datetime.now(timezone.utc)
            if self.metrics_hook:
                self.metrics_hook.on_job_cancelled(self)
            raise
        except Exception as exc:
            self.last_error = str(exc)
            duration_s = asyncio.get_running_loop().time() - started_monotonic

            if self.attempts <= self.max_retries:
                self.state = JobState.RETRYING
                if self.metrics_hook:
                    self.metrics_hook.on_job_retry(self, exc, self.retry_backoff_s)
                if self.retry_backoff_s > 0:
                    await asyncio.sleep(self.retry_backoff_s)
                return await self.execute()

            self.state = JobState.FAILED
            self.last_finished_at = datetime.now(timezone.utc)
            if self.metrics_hook:
                self.metrics_hook.on_job_failed(self, exc, duration_s)
            raise

        self.state = JobState.SUCCEEDED
        self.last_error = None
        self.last_finished_at = datetime.now(timezone.utc)
        duration_s = asyncio.get_running_loop().time() - started_monotonic
        if self.metrics_hook:
            self.metrics_hook.on_job_succeeded(self, duration_s)
        return result

    def cancel(self) -> None:
        self.state = JobState.CANCELLED
        if self.metrics_hook:
            self.metrics_hook.on_job_cancelled(self)
