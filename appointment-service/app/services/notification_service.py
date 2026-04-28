from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationService:
    """Persist notifications. user_id stores the recipient's id (patient_id or doctor_id)."""

    @staticmethod
    def create_for_booking(db: Session, *, patient_id: int, doctor_id: int, date_time: str) -> None:
        db.add(
            Notification(
                user_id=doctor_id,
                message=f"New appointment booked at {date_time}",
            )
        )
        db.add(
            Notification(
                user_id=patient_id,
                message=f"Your appointment is booked at {date_time}",
            )
        )
        db.commit()

    @staticmethod
    def create_for_cancellation(db: Session, *, patient_id: int, doctor_id: int, date_time: str) -> None:
        db.add(
            Notification(
                user_id=doctor_id,
                message=f"Appointment cancelled at {date_time}",
            )
        )
        db.add(
            Notification(
                user_id=patient_id,
                message="Your appointment has been cancelled",
            )
        )
        db.commit()
