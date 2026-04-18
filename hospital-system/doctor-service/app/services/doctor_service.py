import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.doctor import Doctor
from app.schemas.doctor import AvailabilityUpdate, DoctorCreate, DoctorOut, DoctorUpdate, InternalDoctorOut


def _loads_slots(raw: str) -> list[dict[str, Any]]:
    try:
        data = json.loads(raw or "[]")
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


class DoctorService:
    @staticmethod
    def to_out(doctor: Doctor) -> DoctorOut:
        return DoctorOut(
            id=doctor.id,
            name=doctor.name,
            email=doctor.email,
            phone=doctor.phone,
            user_id=doctor.user_id,
            availability=_loads_slots(doctor.availability_json),
        )

    @staticmethod
    def to_internal(doctor: Doctor) -> InternalDoctorOut:
        return InternalDoctorOut(
            id=doctor.id,
            name=doctor.name,
            email=doctor.email,
            availability=_loads_slots(doctor.availability_json),
        )

    @staticmethod
    async def create(db: AsyncSession, payload: DoctorCreate) -> Doctor:
        doctor = Doctor(
            name=payload.name,
            email=str(payload.email),
            phone=payload.phone,
            user_id=payload.user_id,
            availability_json=json.dumps([]),
        )
        db.add(doctor)
        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise ValueError("Email already exists") from exc
        await db.refresh(doctor)
        return doctor

    @staticmethod
    async def update(db: AsyncSession, doctor_id: int, payload: DoctorUpdate) -> Doctor:
        result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
        doctor = result.scalar_one_or_none()
        if doctor is None:
            raise LookupError("Doctor not found")

        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        if "email" in data and data["email"] is not None:
            data["email"] = str(data["email"])
        for key, value in data.items():
            setattr(doctor, key, value)

        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise ValueError("Email already exists") from exc
        await db.refresh(doctor)
        return doctor

    @staticmethod
    async def set_availability(db: AsyncSession, doctor_id: int, payload: AvailabilityUpdate) -> Doctor:
        result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
        doctor = result.scalar_one_or_none()
        if doctor is None:
            raise LookupError("Doctor not found")

        doctor.availability_json = json.dumps([s.model_dump() for s in payload.slots])
        await db.commit()
        await db.refresh(doctor)
        return doctor

    @staticmethod
    async def get(db: AsyncSession, doctor_id: int) -> Doctor | None:
        result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_doctors(db: AsyncSession, limit: int = 100, offset: int = 0) -> list[Doctor]:
        result = await db.execute(select(Doctor).order_by(Doctor.id).limit(limit).offset(offset))
        return list(result.scalars().all())
