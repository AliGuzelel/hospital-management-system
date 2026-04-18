import pytest


@pytest.mark.asyncio
async def test_register_and_login(client):
    reg = await client.post(
        "/auth/register",
        json={"username": "admin1", "password": "password123", "role": "admin"},
    )
    assert reg.status_code == 201, reg.text
    body = reg.json()
    assert "access_token" in body
    assert body["role"] == "admin"

    login = await client.post(
        "/auth/login",
        json={"username": "admin1", "password": "password123"},
    )
    assert login.status_code == 200, login.text
    assert login.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "UP"
