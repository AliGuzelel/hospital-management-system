from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "UP"


def test_create_task():
    response = client.post("/tasks", json={
        "title": "Test Task",
        "description": "Testing task creation"
    })
    assert response.status_code == 200
    assert response.json()["task"]["title"] == "Test Task"


def test_get_tasks():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert "tasks" in response.json()