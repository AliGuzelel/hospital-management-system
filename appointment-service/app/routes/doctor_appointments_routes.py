from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.doctor_appointments import DoctorAppointmentItem
from app.services.doctor_appointment_service import DoctorAppointmentService

router = APIRouter(prefix="/doctors", tags=["doctor-appointments"])


@router.get("/{doctor_id}/appointments", response_model=list[DoctorAppointmentItem])
def list_doctor_appointments(
    doctor_id: int,
    db: Session = Depends(get_db),
    appointment_filter: str | None = Query(
        default=None,
        alias="type",
        description="Filter: 'upcoming' or 'past'",
    ),
):
    try:
        return DoctorAppointmentService.list_for_doctor(db, doctor_id, type_filter=appointment_filter)
    except ValueError as exc:
        detail = str(exc)
        status = 404 if "not found" in detail.lower() else 400
        raise HTTPException(status_code=status, detail=detail) from exc
