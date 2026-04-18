import pytest
from jose import jwt


def _token(*, role: str, sub: int = 1) -> str:
    return jwt.encode({"sub": str(sub), "role": role}, "test-secret", algorithm="HS256")


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_create_doctor_and_availability(client):
    headers = {"Authorization": f"Bearer {_token(role='admin')}"}
    created = await client.post(
        "/doctors",
        headers=headers,
        json={"name": "Dr A", "email": "dra@example.com", "phone": "+15550003"},
    )
    assert created.status_code == 201, created.text
    did = created.json()["id"]

    avail = await client.put(
        f"/doctors/{did}/availability",
        headers=headers,
        json={"slots": [{"weekday": 0, "start": "09:00", "end": "17:00"}]},
    )
    assert avail.status_code == 200, avail.text
    assert avail.json()["availability"][0]["weekday"] == 0
