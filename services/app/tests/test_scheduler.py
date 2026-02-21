import pytest

from app.dependencies import repository, scheduler


@pytest.mark.asyncio
async def test_scheduler_runs_due_jobs() -> None:
    task = await repository.create_task("scrape", {"url": "https://example.com"})
    await repository.create_job(task.id, schedule_every_seconds=1, enabled=True)

    result = await scheduler.run_once()

    assert result["success"] == 1
    assert result["failures"] == 0
    jobs = await repository.list_jobs()
    assert jobs[0].last_run_at is not None
