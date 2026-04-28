import logging

import httpx
from sqlalchemy.orm import Session
from app.config.settings import settings
from app.models.appointment import Appointment
from app.services.event_bus import publish_event_sync
from app.services.invoice_service import InvoiceService
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


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
        try:
            publish_event_sync("appointment.created", {"appointment_id": obj.id, "patient_id": obj.patient_id, "doctor_id": obj.doctor_id})
        except Exception:
            logger.exception("failed_to_publish_appointment_created_event")
        try:
            NotificationService.create_for_booking(
                db,
                patient_id=obj.patient_id,
                doctor_id=obj.doctor_id,
                date_time=obj.date_time,
            )
        except Exception:
            logger.exception("failed_to_create_booking_notifications")
        return obj
    @staticmethod
    def cancel(db: Session, appointment_id: int):
        obj = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not obj:
            return None
        saved_dt = obj.date_time
        saved_patient = obj.patient_id
        saved_doctor = obj.doctor_id
        obj.status = "cancelled"
        db.commit()
        db.refresh(obj)
        try:
            publish_event_sync("appointment.cancelled", {"appointment_id": obj.id})
        except Exception:
            logger.exception("failed_to_publish_appointment_cancelled_event")
        try:
            NotificationService.create_for_cancellation(
                db,
                patient_id=saved_patient,
                doctor_id=saved_doctor,
                date_time=saved_dt,
            )
        except Exception:
            logger.exception("failed_to_create_cancellation_notifications")
        return obj

    @staticmethod
    def complete(db: Session, appointment_id: int):
        obj = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not obj:
            return None
        obj.status = "completed"
        db.commit()
        db.refresh(obj)
        InvoiceService.create_for_completed_appointment(
            db,
            appointment_id=obj.id,
            patient_id=obj.patient_id,
            doctor_id=obj.doctor_id,
        )
        return obj
