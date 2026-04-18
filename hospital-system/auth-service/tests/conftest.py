import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("AUTH_DATABASE_URL", "sqlite+aiosqlite:///:memory:")

from app.database.session import get_session  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import Base  # noqa: E402


@pytest_asyncio.fixture
async def client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestSession = async_sessionmaker(engine, expire_on_commit=False)

    async def _session():
        async with TestSession() as session:
            yield session

    app.dependency_overrides[get_session] = _session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    await engine.dispose()
