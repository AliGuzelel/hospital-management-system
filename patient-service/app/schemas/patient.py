from pydantic import BaseModel, EmailStr
class PatientCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    
class PatientUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    
class PatientOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    
    class Config:
        from_attributes = True
