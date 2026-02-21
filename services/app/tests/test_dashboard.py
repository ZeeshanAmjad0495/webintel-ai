from fastapi.testclient import TestClient


def test_dashboard_page_renders(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "WebIntel AI Dashboard" in response.text
    assert "Sample operational view" in response.text
    assert "fetch('/api/tasks')" in response.text
