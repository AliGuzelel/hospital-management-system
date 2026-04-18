from pydantic import BaseModel, EmailStr
class DoctorCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    availability: str | None = None
class DoctorUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    availability: str | None = None
class DoctorOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    availability: str | None = None
    class Config:
        from_attributes = True
