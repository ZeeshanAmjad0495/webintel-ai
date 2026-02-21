from time import perf_counter

from app.core.metrics import RUN_DURATION_SECONDS
from app.services.repositories import InMemoryRepository


class MonitorService:
    def __init__(self, repository: InMemoryRepository) -> None:
        self.repository = repository

    async def ingest_snapshot(self, monitor_id: str, snapshot: str) -> bool:
        start = perf_counter()
        monitor = await self.repository.set_monitor_snapshot(monitor_id, snapshot)
        RUN_DURATION_SECONDS.labels(operation="monitor_ingest", status="success").observe(perf_counter() - start)
        if monitor is None:
            return False
        return monitor.changed
