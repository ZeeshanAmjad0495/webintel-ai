from time import perf_counter

from app.core.metrics import FAILURE_COUNTER, RUN_DURATION_SECONDS
from app.services.repositories import TaskRecord


class JobExecutor:
    async def execute(self, task: TaskRecord) -> str:
        start = perf_counter()
        operation = "job_execution"
        try:
            if task.payload.get("fail"):
                raise RuntimeError("task payload requested failure")
            result = f"executed:{task.name}"
            RUN_DURATION_SECONDS.labels(operation=operation, status="success").observe(perf_counter() - start)
            return result
        except Exception:
            FAILURE_COUNTER.labels(operation=operation).inc()
            RUN_DURATION_SECONDS.labels(operation=operation, status="failure").observe(perf_counter() - start)
            raise
