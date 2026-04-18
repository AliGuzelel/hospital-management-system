from datetime import datetime

from pydantic import BaseModel, Field, model_validator


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


class AppointmentOut(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    booked_by_user_id: int
    start_time: datetime
    end_time: datetime
    status: str

    model_config = {"from_attributes": True}
