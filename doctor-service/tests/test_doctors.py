from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
def test_create_and_get():
    payload = {"name":"n1","email":"n1@example.com","phone":"111", "availability":"Mon-Fri"}
    created = client.post("/doctors", json=payload)
    assert created.status_code == 200
    fetched = client.get(f"/doctors/{created.json()['id']}")
    assert fetched.status_code == 200
