from fastapi.testclient import TestClient


def test_api_crud_and_scheduler_endpoint(client: TestClient) -> None:
    task_response = client.post("/api/tasks", json={"name": "crawl", "payload": {"depth": 2}})
    assert task_response.status_code == 201
    task_id = task_response.json()["id"]

    job_response = client.post(
        "/api/jobs",
        json={"task_id": task_id, "schedule_every_seconds": 1, "enabled": True},
    )
    assert job_response.status_code == 201

    monitor_response = client.post(
        "/api/monitors",
        json={"name": "landing", "source_url": "https://example.com"},
    )
    assert monitor_response.status_code == 201
    monitor_id = monitor_response.json()["id"]

    snapshot_1 = client.post(f"/api/monitors/{monitor_id}/snapshot", json={"snapshot": "A"})
    snapshot_2 = client.post(f"/api/monitors/{monitor_id}/snapshot", json={"snapshot": "B"})
    assert snapshot_1.status_code == 200
    assert snapshot_1.json()["changed"] is False
    assert snapshot_2.json()["changed"] is True

    run_response = client.post("/api/jobs/run")
    assert run_response.status_code == 200
    assert "success=1" in run_response.json()["details"]

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "job_count" in metrics.text
