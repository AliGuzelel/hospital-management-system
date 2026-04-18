from sqlalchemy import Column, Integer, String
from app.database.session import Base

class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), nullable=False, unique=True)
    phone = Column(String(30), nullable=False)
    availability = Column(String(255), nullable=True)
