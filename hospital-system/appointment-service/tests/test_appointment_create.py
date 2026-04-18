from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models.appointment import Base
from app.schemas.appointment import AppointmentCreate
from app.services.appointment_service import AppointmentService


@pytest.mark.asyncio
async def test_create_appointment_persists(monkeypatch):
    monkeypatch.setattr(
        "app.services.integration.get_patient_internal",
        AsyncMock(return_value={"id": 1, "user_id": 10}),
    )
    monkeypatch.setattr(
        "app.services.integration.get_doctor_internal",
        AsyncMock(
            return_value={
                "id": 2,
                "availability": [{"weekday": 0, "start": "09:00", "end": "18:00"}],
            }
        ),
    )
    monkeypatch.setattr("app.services.events.publish_appointment_created", AsyncMock())

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestSession = async_sessionmaker(engine, expire_on_commit=False)

    exchange = MagicMock()
    exchange.publish = AsyncMock()
    http = MagicMock()

    async with TestSession() as db:
        payload = AppointmentCreate(
            patient_id=1,
            doctor_id=2,
            start_time=datetime(2026, 4, 20, 10, 0, tzinfo=timezone.utc),
            end_time=datetime(2026, 4, 20, 10, 30, tzinfo=timezone.utc),
        )
        appt = await AppointmentService.create(db, http, exchange, payload, booked_by_user_id=10)
        assert appt.id >= 1
        assert appt.status == "scheduled"

    await engine.dispose()
