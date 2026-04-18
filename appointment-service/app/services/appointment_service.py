import httpx
from sqlalchemy.orm import Session
from app.config.settings import settings
from app.models.appointment import Appointment
from app.services.event_bus import publish_event_sync

class AppointmentService:
    @staticmethod
    def _validate_entities(patient_id: int, doctor_id: int):
        p = httpx.get(f"{settings.patient_service_url}/patients/{patient_id}", timeout=5)
        d = httpx.get(f"{settings.doctor_service_url}/doctors/{doctor_id}", timeout=5)
        if p.status_code != 200:
            raise ValueError("Invalid patient")
        if d.status_code != 200:
            raise ValueError("Invalid doctor")
    @staticmethod
    def book(db: Session, data):
        AppointmentService._validate_entities(data.patient_id, data.doctor_id)
        obj = Appointment(patient_id=data.patient_id, doctor_id=data.doctor_id, date_time=data.date_time, status="booked")
        db.add(obj)
        db.commit()
        db.refresh(obj)
        publish_event_sync("appointment.created", {"appointment_id": obj.id, "patient_id": obj.patient_id, "doctor_id": obj.doctor_id})
        return obj
    @staticmethod
    def cancel(db: Session, appointment_id: int):
        obj = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not obj:
            return None
        obj.status = "cancelled"
        db.commit()
        db.refresh(obj)
        publish_event_sync("appointment.cancelled", {"appointment_id": obj.id})
        return obj
