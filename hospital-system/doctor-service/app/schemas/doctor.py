from typing import Any

from pydantic import BaseModel, EmailStr, Field


class AvailabilitySlot(BaseModel):
    weekday: int = Field(..., ge=0, le=6, description="0=Monday ... 6=Sunday (Python weekday)")
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


class DoctorOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    user_id: int | None = None
    availability: list[dict[str, Any]]


class InternalDoctorOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    availability: list[dict[str, Any]]
