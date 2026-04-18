from pydantic import BaseModel
class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    date_time: str
class AppointmentOut(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    date_time: str
    status: str
    class Config:
        from_attributes = True
