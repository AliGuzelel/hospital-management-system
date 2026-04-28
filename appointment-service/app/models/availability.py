from sqlalchemy import Boolean, Column, Integer, String

from app.database.session import Base


class DoctorAvailability(Base):
    __tablename__ = "doctor_availability"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, nullable=False, index=True)
    weekday = Column(Integer, nullable=False)  # Monday=0 ... Sunday=6
    start_time = Column(String(5), nullable=False)  # HH:MM
    end_time = Column(String(5), nullable=False)  # HH:MM
    slot_minutes = Column(Integer, nullable=False, default=30)
    is_active = Column(Boolean, nullable=False, default=True)


class DoctorTimeOff(Base):
    __tablename__ = "doctor_time_off"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, nullable=False, index=True)
    start_datetime = Column(String(32), nullable=False)
    end_datetime = Column(String(32), nullable=False)
    reason = Column(String(255), nullable=True)
