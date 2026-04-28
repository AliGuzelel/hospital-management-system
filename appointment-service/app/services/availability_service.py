from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.availability import DoctorAvailability, DoctorTimeOff


def _parse_iso_datetime(value: str) -> datetime:
    raw = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _parse_hhmm(value: str) -> tuple[int, int]:
    hh, mm = value.split(":")
    return int(hh), int(mm)


class AvailabilityService:
    @staticmethod
    def ensure_doctor_exists(doctor_id: int) -> None:
        r = httpx.get(f"{settings.doctor_service_url}/doctors/{doctor_id}", timeout=5)
        if r.status_code != 200:
            raise ValueError("Doctor not found")

    @staticmethod
    def create_availability(db: Session, data):
        AvailabilityService.ensure_doctor_exists(data.doctor_id)
        obj = DoctorAvailability(
            doctor_id=data.doctor_id,
            weekday=data.weekday,
            start_time=data.start_time,
            end_time=data.end_time,
            slot_minutes=data.slot_minutes,
            is_active=data.is_active,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def list_availability(db: Session, doctor_id: int):
        AvailabilityService.ensure_doctor_exists(doctor_id)
        return (
            db.query(DoctorAvailability)
            .filter(DoctorAvailability.doctor_id == doctor_id)
            .order_by(DoctorAvailability.weekday.asc(), DoctorAvailability.start_time.asc())
            .all()
        )

    @staticmethod
    def create_time_off(db: Session, data):
        AvailabilityService.ensure_doctor_exists(data.doctor_id)
        start_dt = _parse_iso_datetime(data.start_datetime)
        end_dt = _parse_iso_datetime(data.end_datetime)
        if end_dt <= start_dt:
            raise ValueError("end_datetime must be after start_datetime")
        obj = DoctorTimeOff(
            doctor_id=data.doctor_id,
            start_datetime=data.start_datetime,
            end_datetime=data.end_datetime,
            reason=data.reason,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def is_slot_available(db: Session, doctor_id: int, when_iso: str) -> bool:
        when = _parse_iso_datetime(when_iso)
        slots = (
            db.query(DoctorAvailability)
            .filter(
                DoctorAvailability.doctor_id == doctor_id,
                DoctorAvailability.weekday == when.weekday(),
                DoctorAvailability.is_active == True,  # noqa: E712
            )
            .all()
        )
        if not slots:
            return False

        in_window = False
        for slot in slots:
            start_h, start_m = _parse_hhmm(slot.start_time)
            end_h, end_m = _parse_hhmm(slot.end_time)
            start_minutes = start_h * 60 + start_m
            end_minutes = end_h * 60 + end_m
            current_minutes = when.hour * 60 + when.minute
            if start_minutes <= current_minutes < end_minutes:
                in_window = True
                break
        if not in_window:
            return False

        time_off_rows = (
            db.query(DoctorTimeOff).filter(DoctorTimeOff.doctor_id == doctor_id).all()
        )
        for row in time_off_rows:
            start = _parse_iso_datetime(row.start_datetime)
            end = _parse_iso_datetime(row.end_datetime)
            if start <= when < end:
                return False
        return True

    @staticmethod
    def suggest_slots(
        db: Session, doctor_id: int, from_iso: str, to_iso: str, limit: int = 10
    ) -> list[str]:
        AvailabilityService.ensure_doctor_exists(doctor_id)
        start = _parse_iso_datetime(from_iso)
        end = _parse_iso_datetime(to_iso)
        if end <= start:
            raise ValueError("to must be after from")

        result: list[str] = []
        cursor = start
        while cursor < end and len(result) < limit:
            as_iso = cursor.isoformat()
            if AvailabilityService.is_slot_available(db, doctor_id, as_iso):
                result.append(as_iso)
            cursor = cursor + timedelta(minutes=30)
        return result
