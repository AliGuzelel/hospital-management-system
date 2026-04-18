from pydantic import BaseModel, ConfigDict, Field


class RegisterBody(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"username": "patient1", "password": "secret12", "role": "patient"}
        }
    )

    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    role: str


class LoginBody(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"example": {"username": "patient1", "password": "secret12"}}
    )

    username: str
    password: str


class PatientCreateBody(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Jane Doe",
                "email": "jane@example.com",
                "phone": "+15551234567",
            }
        }
    )

    name: str
    email: str
    phone: str


class PatientUpdateBody(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"name": "Jane D.", "email": "jane.d@example.com", "phone": "+15559876543"}
        }
    )

    name: str | None = None
    email: str | None = None
    phone: str | None = None


class DoctorCreateBody(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Dr. Smith",
                "email": "smith@example.com",
                "phone": "+15550001111",
                "availability": "Mon-Fri 9-17",
            }
        }
    )

    name: str
    email: str
    phone: str
    availability: str | None = None


class DoctorUpdateBody(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"example": {"availability": "Mon/Wed 10-14"}}
    )

    name: str | None = None
    email: str | None = None
    phone: str | None = None
    availability: str | None = None


class AppointmentCreateBody(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "patient_id": 1,
                "doctor_id": 1,
                "date_time": "2026-04-20T14:30:00",
            }
        }
    )

    patient_id: int
    doctor_id: int
    date_time: str
