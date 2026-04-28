from datetime import datetime

from sqlalchemy import Column, Float, Integer, String

from app.database.session import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, nullable=False, unique=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    doctor_id = Column(Integer, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(8), nullable=False, default="USD")
    status = Column(String(32), nullable=False, default="pending")
    created_at = Column(String(32), nullable=False, default=lambda: datetime.utcnow().isoformat())
    paid_at = Column(String(32), nullable=True)
