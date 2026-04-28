from pydantic import BaseModel


class DoctorAppointmentItem(BaseModel):
    id: int
    patient_id: int
    date_time: str
    status: str

    model_config = {"from_attributes": True}
