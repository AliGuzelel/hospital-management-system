import pytest
from jose import jwt


def _token(*, role: str, sub: int = 1) -> str:
    return jwt.encode({"sub": str(sub), "role": role}, "test-secret", algorithm="HS256")


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_create_and_get_patient(client):
    headers = {"Authorization": f"Bearer {_token(role='admin')}"}
    created = await client.post(
        "/patients",
        headers=headers,
        json={"name": "Alice", "email": "alice@example.com", "phone": "+15550001"},
    )
    assert created.status_code == 201, created.text
    pid = created.json()["id"]

    got = await client.get(f"/patients/{pid}", headers=headers)
    assert got.status_code == 200
    assert got.json()["email"] == "alice@example.com"


@pytest.mark.asyncio
async def test_internal_patient(client):
    headers = {"Authorization": f"Bearer {_token(role='admin')}"}
    created = await client.post(
        "/patients",
        headers=headers,
        json={"name": "Bob", "email": "bob@example.com", "phone": "+15550002"},
    )
    pid = created.json()["id"]

    r = await client.get(
        f"/internal/patients/{pid}",
        headers={"X-Service-Token": "internal-token"},
    )
    assert r.status_code == 200
    assert r.json()["id"] == pid
