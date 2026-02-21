import pytest

from app.dependencies import monitor_service, repository


@pytest.mark.asyncio
async def test_monitor_change_detection() -> None:
    monitor = await repository.create_monitor("home", "https://example.com")

    first_change = await monitor_service.ingest_snapshot(monitor.id, "<html>v1</html>")
    second_change = await monitor_service.ingest_snapshot(monitor.id, "<html>v1</html>")
    third_change = await monitor_service.ingest_snapshot(monitor.id, "<html>v2</html>")

    assert first_change is False
    assert second_change is False
    assert third_change is True
