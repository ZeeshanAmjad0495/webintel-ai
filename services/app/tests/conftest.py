import pytest
from fastapi.testclient import TestClient

from app.dependencies import repository
from app.main import app


@pytest.fixture(autouse=True)
async def reset_repository() -> None:
    await repository.reset()
    yield
    await repository.reset()


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)
