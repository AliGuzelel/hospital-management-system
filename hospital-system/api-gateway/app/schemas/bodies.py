from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, model_validator


class Role(str, Enum):
    admin = "admin"
    doctor = "doctor"
    patient = "patient"


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=8, max_length=128)
    role: Role


class LoginRequest(BaseModel):
    username: str
    password: str


class PatientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    email: EmailStr
    phone: str = Field(..., min_length=3, max_length=64)
    user_id: int | None = None


class PatientUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=3, max_length=64)
    user_id: int | None = None


class AvailabilitySlot(BaseModel):
    weekday: int = Field(..., ge=0, le=6)
    start: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    end: str = Field(..., pattern=r"^\d{2}:\d{2}$")


class DoctorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    email: EmailStr
    phone: str = Field(..., min_length=3, max_length=64)
    user_id: int | None = None


class DoctorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=3, max_length=64)
    user_id: int | None = None


class AvailabilityUpdate(BaseModel):
    slots: list[AvailabilitySlot]


class AppointmentCreate(BaseModel):
    patient_id: int = Field(..., ge=1)
    doctor_id: int = Field(..., ge=1)
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def validate_range(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self
