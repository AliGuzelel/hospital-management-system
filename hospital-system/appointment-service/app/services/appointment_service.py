from __future__ import annotations

import logging

import httpx
from aio_pika import Exchange
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate
from app.services import events, integration
from app.utils.availability import fits_doctor_availability

logger = logging.getLogger(__name__)


class AppointmentService:
    @staticmethod
    async def create(
        db: AsyncSession,
        http: httpx.AsyncClient,
        exchange: Exchange,
        payload: AppointmentCreate,
        booked_by_user_id: int,
    ) -> Appointment:
        try:
            await integration.get_patient_internal(
                http,
                settings.patient_service_url,
                payload.patient_id,
                settings.internal_service_token,
            )
        except LookupError as exc:
            raise ValueError(str(exc)) from exc

        try:
            doctor = await integration.get_doctor_internal(
                http,
                settings.doctor_service_url,
                payload.doctor_id,
                settings.internal_service_token,
            )
        except LookupError as exc:
            raise ValueError(str(exc)) from exc

        slots = doctor.get("availability") or []
        if not fits_doctor_availability(payload.start_time, payload.end_time, slots):
            raise ValueError("Requested time is outside doctor availability")

        overlap = await db.execute(
            select(Appointment.id)
            .where(
                and_(
                    Appointment.doctor_id == payload.doctor_id,
                    Appointment.status == "scheduled",
                    Appointment.start_time < payload.end_time,
                    Appointment.end_time > payload.start_time,
                )
            )
            .limit(1)
        )
        if overlap.scalar_one_or_none() is not None:
            raise ValueError("Doctor already has a scheduled appointment in this window")

        appt = Appointment(
            patient_id=payload.patient_id,
            doctor_id=payload.doctor_id,
            booked_by_user_id=booked_by_user_id,
            start_time=payload.start_time,
            end_time=payload.end_time,
            status="scheduled",
        )
        db.add(appt)
        await db.commit()
        await db.refresh(appt)

        event_payload = {
            "event": "appointment_created",
            "appointment_id": appt.id,
            "patient_id": appt.patient_id,
            "doctor_id": appt.doctor_id,
            "start_time": appt.start_time.isoformat(),
            "end_time": appt.end_time.isoformat(),
        }
        try:
            await events.publish_appointment_created(exchange, event_payload)
        except Exception:  # noqa: BLE001
            logger.exception("failed_to_publish_appointment_event appointment_id=%s", appt.id)

        return appt

    @staticmethod
    async def cancel(
        db: AsyncSession,
        http: httpx.AsyncClient,
        appointment_id: int,
        user: dict,
    ) -> Appointment:
        result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
        appt = result.scalar_one_or_none()
        if appt is None:
            raise LookupError("Appointment not found")
        if appt.status != "scheduled":
            raise ValueError("Appointment is not active")

        role = user.get("role")
        sub = int(user.get("sub", 0))

        if role == "admin":
            pass
        elif role == "patient":
            patient = await integration.get_patient_internal(
                http,
                settings.patient_service_url,
                appt.patient_id,
                settings.internal_service_token,
            )
            if patient.get("user_id") is None or int(patient["user_id"]) != sub:
                raise PermissionError("Cannot cancel this appointment")
        elif role == "doctor":
            doctor = await integration.get_doctor_internal(
                http,
                settings.doctor_service_url,
                appt.doctor_id,
                settings.internal_service_token,
            )
            if doctor.get("user_id") is None or int(doctor["user_id"]) != sub:
                raise PermissionError("Cannot cancel this appointment")
        else:
            raise PermissionError("Cannot cancel this appointment")

        appt.status = "cancelled"
        await db.commit()
        await db.refresh(appt)
        return appt

    @staticmethod
    async def list_appointments(
        db: AsyncSession,
        http: httpx.AsyncClient,
        user: dict,
        patient_id: int | None,
        doctor_id: int | None,
        limit: int,
        offset: int,
    ) -> list[Appointment]:
        role = user.get("role")
        sub = int(user.get("sub", 0))

        stmt = select(Appointment)

        if role == "admin":
            filters: list = []
            if patient_id is not None:
                filters.append(Appointment.patient_id == patient_id)
            if doctor_id is not None:
                filters.append(Appointment.doctor_id == doctor_id)
            if filters:
                stmt = stmt.where(and_(*filters))
            stmt = stmt.order_by(Appointment.start_time.desc()).limit(limit).offset(offset)
            result = await db.execute(stmt)
            return list(result.scalars().all())

        if role == "patient":
            if patient_id is None:
                raise ValueError("patient_id is required")
            patient = await integration.get_patient_internal(
                http,
                settings.patient_service_url,
                patient_id,
                settings.internal_service_token,
            )
            if patient.get("user_id") is None or int(patient["user_id"]) != sub:
                raise PermissionError("Cannot list appointments for this patient")
            stmt = (
                stmt.where(Appointment.patient_id == patient_id)
                .order_by(Appointment.start_time.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await db.execute(stmt)
            return list(result.scalars().all())

        if role == "doctor":
            if doctor_id is None:
                raise ValueError("doctor_id is required")
            doctor = await integration.get_doctor_internal(
                http,
                settings.doctor_service_url,
                doctor_id,
                settings.internal_service_token,
            )
            if doctor.get("user_id") is None or int(doctor["user_id"]) != sub:
                raise PermissionError("Cannot list appointments for this doctor")
            stmt = (
                stmt.where(Appointment.doctor_id == doctor_id)
                .order_by(Appointment.start_time.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await db.execute(stmt)
            return list(result.scalars().all())

        raise PermissionError("Insufficient permissions")
