from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.invoice import Invoice


class InvoiceService:
    @staticmethod
    def create_for_completed_appointment(
        db: Session,
        *,
        appointment_id: int,
        patient_id: int,
        doctor_id: int,
        amount: float = 100.0,
        currency: str = "USD",
    ) -> Invoice:
        existing = (
            db.query(Invoice).filter(Invoice.appointment_id == appointment_id).first()
        )
        if existing:
            return existing

        obj = Invoice(
            appointment_id=appointment_id,
            patient_id=patient_id,
            doctor_id=doctor_id,
            amount=amount,
            currency=currency,
            status="pending",
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def list_invoices(
        db: Session,
        *,
        patient_id: int | None = None,
        doctor_id: int | None = None,
        status: str | None = None,
    ) -> list[Invoice]:
        q = db.query(Invoice)
        if patient_id is not None:
            q = q.filter(Invoice.patient_id == patient_id)
        if doctor_id is not None:
            q = q.filter(Invoice.doctor_id == doctor_id)
        if status is not None:
            q = q.filter(Invoice.status == status)
        return q.order_by(Invoice.id.desc()).all()

    @staticmethod
    def get_invoice(db: Session, invoice_id: int) -> Invoice | None:
        return db.query(Invoice).filter(Invoice.id == invoice_id).first()

    @staticmethod
    def mark_paid(db: Session, invoice_id: int) -> Invoice | None:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            return None
        invoice.status = "paid"
        invoice.paid_at = datetime.now(timezone.utc).isoformat()
        db.commit()
        db.refresh(invoice)
        return invoice
