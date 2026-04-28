from pydantic import BaseModel, Field, field_validator


class DoctorAvailabilityCreate(BaseModel):
    doctor_id: int = Field(..., ge=1)
    weekday: int = Field(..., ge=0, le=6)
    start_time: str
    end_time: str
    slot_minutes: int = Field(default=30, ge=5, le=240)
    is_active: bool = True

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time_format(cls, value: str) -> str:
        if len(value) != 5 or value[2] != ":":
            raise ValueError("time must be in HH:MM format")
        hh, mm = value.split(":")
        if not (hh.isdigit() and mm.isdigit()):
            raise ValueError("time must be in HH:MM format")
        h, m = int(hh), int(mm)
        if h < 0 or h > 23 or m < 0 or m > 59:
            raise ValueError("time must be in HH:MM format")
        return value


class DoctorAvailabilityOut(BaseModel):
    id: int
    doctor_id: int
    weekday: int
    start_time: str
    end_time: str
    slot_minutes: int
    is_active: bool

    model_config = {"from_attributes": True}


class DoctorTimeOffCreate(BaseModel):
    doctor_id: int = Field(..., ge=1)
    start_datetime: str
    end_datetime: str
    reason: str | None = None


class DoctorTimeOffOut(BaseModel):
    id: int
    doctor_id: int
    start_datetime: str
    end_datetime: str
    reason: str | None = None

    model_config = {"from_attributes": True}
