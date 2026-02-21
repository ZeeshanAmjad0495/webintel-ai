from datetime import datetime, timezone
from time import perf_counter

from app.core.metrics import FAILURE_COUNTER, RUN_DURATION_SECONDS
from app.services.executor import JobExecutor
from app.services.repositories import InMemoryRepository


class Scheduler:
    def __init__(self, repository: InMemoryRepository, executor: JobExecutor) -> None:
        self.repository = repository
        self.executor = executor

    async def run_once(self) -> dict[str, int]:
        start = perf_counter()
        success = 0
        failures = 0
        now = datetime.now(timezone.utc)
        for job in await self.repository.list_jobs():
            if not job.enabled:
                continue
            due = job.last_run_at is None or (now - job.last_run_at).total_seconds() >= job.schedule_every_seconds
            if not due:
                continue
            task = await self.repository.get_task(job.task_id)
            if not task:
                failures += 1
                FAILURE_COUNTER.labels(operation="scheduler_missing_task").inc()
                continue
            try:
                await self.executor.execute(task)
                await self.repository.mark_job_run(job.id)
                success += 1
            except Exception:
                failures += 1
                FAILURE_COUNTER.labels(operation="scheduler_execution").inc()
        status = "success" if failures == 0 else "failure"
        RUN_DURATION_SECONDS.labels(operation="scheduler_run", status=status).observe(perf_counter() - start)
        return {"success": success, "failures": failures}
