from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.appointment import AppointmentCreate, AppointmentOut
from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.post("", response_model=AppointmentOut)
def book(data: AppointmentCreate, db: Session = Depends(get_db)):
    try:
        return AppointmentService.book(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@router.delete("/{appointment_id}", response_model=AppointmentOut)
def cancel(appointment_id: int, db: Session = Depends(get_db)):
    result = AppointmentService.cancel(db, appointment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return result


@router.post("/{appointment_id}/complete", response_model=AppointmentOut)
def complete(appointment_id: int, db: Session = Depends(get_db)):
    result = AppointmentService.complete(db, appointment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return result
