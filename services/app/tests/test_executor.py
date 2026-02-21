import pytest

from app.dependencies import executor, repository


@pytest.mark.asyncio
async def test_job_execution_success_and_failure() -> None:
    success_task = await repository.create_task("ok", {"value": 1})
    fail_task = await repository.create_task("bad", {"fail": True})

    success_result = await executor.execute(success_task)
    assert success_result == "executed:ok"

    with pytest.raises(RuntimeError):
        await executor.execute(fail_task)
