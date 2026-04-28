from pydantic import BaseModel


class InvoiceOut(BaseModel):
    id: int
    appointment_id: int
    patient_id: int
    doctor_id: int
    amount: float
    currency: str
    status: str
    created_at: str
    paid_at: str | None = None

    model_config = {"from_attributes": True}
