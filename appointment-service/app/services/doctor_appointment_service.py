from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.appointment import Appointment
from app.schemas.doctor_appointments import DoctorAppointmentItem


def _parse_appointment_datetime(date_time: str) -> datetime:
    raw = date_time.replace("Z", "+00:00")
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


class DoctorAppointmentService:
    @staticmethod
    def ensure_doctor_exists(doctor_id: int) -> None:
        r = httpx.get(f"{settings.doctor_service_url}/doctors/{doctor_id}", timeout=5)
        if r.status_code != 200:
            raise ValueError("Doctor not found")

    @staticmethod
    def list_for_doctor(
        db: Session,
        doctor_id: int,
        *,
        type_filter: str | None = None,
    ) -> list[DoctorAppointmentItem]:
        DoctorAppointmentService.ensure_doctor_exists(doctor_id)
        q = db.query(Appointment).filter(Appointment.doctor_id == doctor_id).order_by(Appointment.date_time.desc())
        rows = q.all()
        if type_filter not in (None, "upcoming", "past"):
            raise ValueError("type must be 'upcoming', 'past', or omitted")

        if type_filter is None:
            return [DoctorAppointmentItem.model_validate(a) for a in rows]

        now = datetime.now(timezone.utc)
        filtered: list[Appointment] = []
        for a in rows:
            try:
                dt = _parse_appointment_datetime(a.date_time)
            except ValueError:
                continue
            if type_filter == "upcoming" and dt >= now:
                filtered.append(a)
            elif type_filter == "past" and dt < now:
                filtered.append(a)
        return [DoctorAppointmentItem.model_validate(a) for a in filtered]
