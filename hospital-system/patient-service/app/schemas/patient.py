from pydantic import BaseModel, EmailStr, Field


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


class PatientOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    user_id: int | None = None

    model_config = {"from_attributes": True}


class InternalPatientOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    user_id: int | None = None
