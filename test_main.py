from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_add_task():
    response = client.post("/api/tasks", json={"title": "Tester TaskFlow"})
    assert response.status_code == 201
    assert "Tester TaskFlow" in client.get("/api/tasks").json()
