from sqlalchemy import Column, Integer, String
from app.database.session import Base
class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    doctor_id = Column(Integer, nullable=False)
    date_time = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="booked")
