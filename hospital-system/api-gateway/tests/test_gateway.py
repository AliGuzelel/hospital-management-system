import pytest
from httpx import ASGITransport, AsyncClient
from starlette.responses import Response

from app.main import app


@pytest.mark.asyncio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/health")
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_login_forwards(monkeypatch):
    async def fake_proxy(*args, **kwargs):
        return Response(
            content=b'{"access_token":"x","token_type":"bearer","expires_in":3600,"role":"admin","user_id":1}',
            media_type="application/json",
            status_code=200,
        )

    monkeypatch.setattr("app.routes.gateway.proxy_request", fake_proxy)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post("/auth/login", json={"username": "u", "password": "p"})
        assert r.status_code == 200
        assert r.json()["access_token"] == "x"
