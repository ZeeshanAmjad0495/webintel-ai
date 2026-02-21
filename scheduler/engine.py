from __future__ import annotations

import asyncio
import heapq
import itertools
from dataclasses import dataclass
from typing import Dict, Optional

from scheduler.job import Job


@dataclass(slots=True)
class ScheduledJob:
    id: str
    job: Job
    run_at: float
    interval_s: Optional[float] = None
    cancelled: bool = False


class SchedulerEngine:
    """Heap-based async scheduler with wakeups and recurring job support."""

    def __init__(self) -> None:
        self._heap: list[tuple[float, int, str]] = []
        self._jobs: Dict[str, ScheduledJob] = {}
        self._sequence = itertools.count()
        self._wake_event = asyncio.Event()
        self._stop_event = asyncio.Event()
        self._running_tasks: Dict[str, asyncio.Task[None]] = {}

    def schedule(self, job: Job, *, delay_s: float = 0.0, interval_s: Optional[float] = None) -> str:
        loop = asyncio.get_running_loop()
        run_at = loop.time() + max(delay_s, 0.0)
        scheduled = ScheduledJob(id=job.id, job=job, run_at=run_at, interval_s=interval_s)
        self._jobs[job.id] = scheduled
        heapq.heappush(self._heap, (run_at, next(self._sequence), job.id))
        self._wake_event.set()
        return job.id

    def cancel(self, job_id: str) -> bool:
        scheduled = self._jobs.get(job_id)
        if not scheduled:
            return False

        scheduled.cancelled = True
        task = self._running_tasks.get(job_id)
        if task and not task.done():
            task.cancel()
        scheduled.job.cancel()
        self._wake_event.set()
        return True

    async def stop(self) -> None:
        self._stop_event.set()
        self._wake_event.set()
        for task in list(self._running_tasks.values()):
            if not task.done():
                task.cancel()

    async def run_forever(self) -> None:
        while not self._stop_event.is_set():
            if not self._heap:
                await self._wait_for_wakeup()
                continue

            run_at, _, job_id = self._heap[0]
            now = asyncio.get_running_loop().time()
            delay = run_at - now

            if delay > 0:
                await self._wait_for_wakeup(timeout=delay)
                continue

            heapq.heappop(self._heap)
            scheduled = self._jobs.get(job_id)
            if not scheduled or scheduled.cancelled:
                self._jobs.pop(job_id, None)
                continue

            task = asyncio.create_task(self._execute_job(scheduled))
            self._running_tasks[job_id] = task

    async def _execute_job(self, scheduled: ScheduledJob) -> None:
        try:
            await scheduled.job.execute()
        except asyncio.CancelledError:
            pass
        except Exception:
            # Failure status is tracked by the Job lifecycle itself.
            pass
        finally:
            self._running_tasks.pop(scheduled.id, None)

            if scheduled.cancelled:
                self._jobs.pop(scheduled.id, None)
                return

            if scheduled.interval_s and scheduled.interval_s > 0:
                scheduled.run_at = asyncio.get_running_loop().time() + scheduled.interval_s
                heapq.heappush(self._heap, (scheduled.run_at, next(self._sequence), scheduled.id))
                self._wake_event.set()
            else:
                self._jobs.pop(scheduled.id, None)

    async def _wait_for_wakeup(self, timeout: Optional[float] = None) -> None:
        self._wake_event.clear()
        try:
            if timeout is None:
                await self._wake_event.wait()
            else:
                await asyncio.wait_for(self._wake_event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            return
