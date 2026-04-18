from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
@patch("app.services.proxy_service.ProxyService.forward")
def test_login_route(mock_forward):
    mock_forward.return_value = {"access_token": "x", "token_type": "bearer", "role": "admin"}
    res = client.post("/auth/login", json={"username": "admin", "password": "secret"})
    assert res.status_code == 200
