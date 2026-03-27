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


def test_login_success():
    response = client.post("/login", json={
        "username": "ali",
        "password": "1234"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_failure():
    response = client.post("/login", json={
        "username": "ali",
        "password": "wrong"
    })
    assert response.status_code == 401