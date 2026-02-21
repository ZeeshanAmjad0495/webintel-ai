from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional, Protocol

from analysis.llm import AnalysisOutput, analyze_monitor_change
from monitors.tasks import diff_hashes, fetch_monitor_target
from scheduler.engine import SchedulerEngine
from scheduler.job import Job


@dataclass(slots=True)
class MonitorSnapshot:
    monitor_id: str
    url: str
    fetched_at: datetime
    status_code: int
    content: str
    content_hash: str
    has_changed: bool


class MonitorRepository(Protocol):
    @asynccontextmanager
    async def transaction(self) -> AsyncIterator["MonitorRepository"]: ...

    async def get_latest_snapshot(self, monitor_id: str) -> Optional[MonitorSnapshot]: ...

    async def save_snapshot(self, snapshot: MonitorSnapshot) -> None: ...

    async def save_analysis(self, monitor_id: str, content_hash: str, analysis: AnalysisOutput) -> None: ...


class InMemoryMonitorRepository:
    """In-memory transactional store suitable for dev/testing."""

    def __init__(self) -> None:
        self._snapshots: Dict[str, List[MonitorSnapshot]] = {}
        self._analyses: Dict[tuple[str, str], dict[str, Any]] = {}
        self._tx_lock = asyncio.Lock()

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator["InMemoryMonitorRepository"]:
        async with self._tx_lock:
            yield self

    async def get_latest_snapshot(self, monitor_id: str) -> Optional[MonitorSnapshot]:
        entries = self._snapshots.get(monitor_id)
        return entries[-1] if entries else None

    async def save_snapshot(self, snapshot: MonitorSnapshot) -> None:
        self._snapshots.setdefault(snapshot.monitor_id, []).append(snapshot)

    async def save_analysis(self, monitor_id: str, content_hash: str, analysis: AnalysisOutput) -> None:
        self._analyses[(monitor_id, content_hash)] = analysis.to_dict()


class MonitorPipeline:
    def __init__(self, *, scheduler: SchedulerEngine, repository: MonitorRepository) -> None:
        self.scheduler = scheduler
        self.repository = repository

    def build_monitor_job(self, *, monitor_id: str, url: str) -> Job:
        async def handler() -> None:
            fetch_result = await fetch_monitor_target(url)
            latest = await self.repository.get_latest_snapshot(monitor_id)
            diff = diff_hashes(
                previous_hash=(latest.content_hash if latest else None),
                current_hash=fetch_result.content_hash,
            )

            snapshot = MonitorSnapshot(
                monitor_id=monitor_id,
                url=url,
                fetched_at=fetch_result.fetched_at,
                status_code=fetch_result.status_code,
                content=fetch_result.content,
                content_hash=fetch_result.content_hash,
                has_changed=diff.has_changed,
            )

            async with self.repository.transaction() as tx:
                await tx.save_snapshot(snapshot)
                self._enqueue_analysis_job(
                    monitor_id=monitor_id,
                    url=url,
                    previous_content=(latest.content if latest else None),
                    current_content=fetch_result.content,
                    content_hash=fetch_result.content_hash,
                )

        return Job(id=f"monitor:{monitor_id}", handler=handler)

    def _enqueue_analysis_job(
        self,
        *,
        monitor_id: str,
        url: str,
        previous_content: str | None,
        current_content: str,
        content_hash: str,
    ) -> None:
        async def analysis_handler() -> None:
            analysis = analyze_monitor_change(
                url=url,
                previous_content=previous_content,
                current_content=current_content,
            )
            async with self.repository.transaction() as tx:
                await tx.save_analysis(monitor_id, content_hash, analysis)

        analysis_job = Job(id=f"analysis:{monitor_id}:{content_hash[:12]}", handler=analysis_handler)
        self.scheduler.schedule(analysis_job)

    async def run_once(self, *, monitor_id: str, url: str) -> None:
        job = self.build_monitor_job(monitor_id=monitor_id, url=url)
        await job.execute()
