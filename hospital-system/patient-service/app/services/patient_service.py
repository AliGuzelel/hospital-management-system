from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate


class PatientService:
    @staticmethod
    async def create(db: AsyncSession, payload: PatientCreate) -> Patient:
        patient = Patient(
            name=payload.name,
            email=str(payload.email),
            phone=payload.phone,
            user_id=payload.user_id,
        )
        db.add(patient)
        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise ValueError("Email already exists") from exc
        await db.refresh(patient)
        return patient

    @staticmethod
    async def update(db: AsyncSession, patient_id: int, payload: PatientUpdate) -> Patient:
        result = await db.execute(select(Patient).where(Patient.id == patient_id))
        patient = result.scalar_one_or_none()
        if patient is None:
            raise LookupError("Patient not found")

        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        if "email" in data and data["email"] is not None:
            data["email"] = str(data["email"])
        for key, value in data.items():
            setattr(patient, key, value)

        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise ValueError("Email already exists") from exc
        await db.refresh(patient)
        return patient

    @staticmethod
    async def get(db: AsyncSession, patient_id: int) -> Patient | None:
        result = await db.execute(select(Patient).where(Patient.id == patient_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_patients(db: AsyncSession, limit: int = 100, offset: int = 0) -> list[Patient]:
        result = await db.execute(select(Patient).order_by(Patient.id).limit(limit).offset(offset))
        return list(result.scalars().all())
