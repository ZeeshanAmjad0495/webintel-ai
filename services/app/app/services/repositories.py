import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any
from uuid import uuid4

from app.core.metrics import JOB_COUNT, MONITOR_COUNT, TASK_COUNT


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class TaskRecord:
    id: str
    name: str
    payload: dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass
class JobRecord:
    id: str
    task_id: str
    schedule_every_seconds: int
    enabled: bool
    last_run_at: datetime | None
    created_at: datetime
    updated_at: datetime


@dataclass
class MonitorRecord:
    id: str
    name: str
    source_url: str
    last_snapshot_hash: str | None = None
    changed: bool = False
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)


class InMemoryRepository:
    def __init__(self) -> None:
        self._tasks: dict[str, TaskRecord] = {}
        self._jobs: dict[str, JobRecord] = {}
        self._monitors: dict[str, MonitorRecord] = {}
        self._lock = asyncio.Lock()

    async def reset(self) -> None:
        async with self._lock:
            self._tasks.clear()
            self._jobs.clear()
            self._monitors.clear()
            TASK_COUNT.set(0)
            JOB_COUNT.set(0)
            MONITOR_COUNT.set(0)

    async def create_task(self, name: str, payload: dict[str, Any]) -> TaskRecord:
        async with self._lock:
            now = utcnow()
            record = TaskRecord(str(uuid4()), name, payload, now, now)
            self._tasks[record.id] = record
            TASK_COUNT.set(len(self._tasks))
            return record

    async def list_tasks(self) -> list[TaskRecord]:
        return list(self._tasks.values())

    async def get_task(self, task_id: str) -> TaskRecord | None:
        return self._tasks.get(task_id)

    async def update_task(self, task_id: str, **updates: Any) -> TaskRecord | None:
        async with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return None
            if "name" in updates and updates["name"] is not None:
                task.name = updates["name"]
            if "payload" in updates and updates["payload"] is not None:
                task.payload = updates["payload"]
            task.updated_at = utcnow()
            return task

    async def delete_task(self, task_id: str) -> bool:
        async with self._lock:
            deleted = self._tasks.pop(task_id, None) is not None
            TASK_COUNT.set(len(self._tasks))
            return deleted

    async def create_job(self, task_id: str, schedule_every_seconds: int, enabled: bool) -> JobRecord:
        async with self._lock:
            now = utcnow()
            record = JobRecord(
                id=str(uuid4()),
                task_id=task_id,
                schedule_every_seconds=schedule_every_seconds,
                enabled=enabled,
                last_run_at=None,
                created_at=now,
                updated_at=now,
            )
            self._jobs[record.id] = record
            JOB_COUNT.set(len(self._jobs))
            return record

    async def list_jobs(self) -> list[JobRecord]:
        return list(self._jobs.values())

    async def get_job(self, job_id: str) -> JobRecord | None:
        return self._jobs.get(job_id)

    async def update_job(self, job_id: str, **updates: Any) -> JobRecord | None:
        async with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            if "schedule_every_seconds" in updates and updates["schedule_every_seconds"] is not None:
                job.schedule_every_seconds = updates["schedule_every_seconds"]
            if "enabled" in updates and updates["enabled"] is not None:
                job.enabled = updates["enabled"]
            job.updated_at = utcnow()
            return job

    async def delete_job(self, job_id: str) -> bool:
        async with self._lock:
            deleted = self._jobs.pop(job_id, None) is not None
            JOB_COUNT.set(len(self._jobs))
            return deleted

    async def mark_job_run(self, job_id: str) -> JobRecord | None:
        async with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            now = utcnow()
            job.last_run_at = now
            job.updated_at = now
            return job

    async def create_monitor(self, name: str, source_url: str) -> MonitorRecord:
        async with self._lock:
            now = utcnow()
            record = MonitorRecord(id=str(uuid4()), name=name, source_url=source_url, created_at=now, updated_at=now)
            self._monitors[record.id] = record
            MONITOR_COUNT.set(len(self._monitors))
            return record

    async def list_monitors(self) -> list[MonitorRecord]:
        return list(self._monitors.values())

    async def get_monitor(self, monitor_id: str) -> MonitorRecord | None:
        return self._monitors.get(monitor_id)

    async def update_monitor(self, monitor_id: str, **updates: Any) -> MonitorRecord | None:
        async with self._lock:
            monitor = self._monitors.get(monitor_id)
            if not monitor:
                return None
            if "name" in updates and updates["name"] is not None:
                monitor.name = updates["name"]
            if "source_url" in updates and updates["source_url"] is not None:
                monitor.source_url = updates["source_url"]
            monitor.updated_at = utcnow()
            return monitor

    async def set_monitor_snapshot(self, monitor_id: str, snapshot: str) -> MonitorRecord | None:
        async with self._lock:
            monitor = self._monitors.get(monitor_id)
            if not monitor:
                return None
            digest = sha256(snapshot.encode("utf-8")).hexdigest()
            monitor.changed = monitor.last_snapshot_hash not in (None, digest)
            monitor.last_snapshot_hash = digest
            monitor.updated_at = utcnow()
            return monitor

    async def delete_monitor(self, monitor_id: str) -> bool:
        async with self._lock:
            deleted = self._monitors.pop(monitor_id, None) is not None
            MONITOR_COUNT.set(len(self._monitors))
            return deleted
