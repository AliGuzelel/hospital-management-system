from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_auth_flow():
    client.post("/auth/register", json={"username": "u1", "password": "secret12", "role": "patient"})
    login = client.post("/auth/login", json={"username": "u1", "password": "secret12"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    check = client.get("/auth/validate", params={"token": token})
    assert check.status_code == 200
