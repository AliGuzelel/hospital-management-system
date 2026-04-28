from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.availability import (
    DoctorAvailabilityCreate,
    DoctorAvailabilityOut,
    DoctorTimeOffCreate,
    DoctorTimeOffOut,
)
from app.services.availability_service import AvailabilityService

router = APIRouter(prefix="/doctors", tags=["availability"])


@router.post("/{doctor_id}/availability", response_model=DoctorAvailabilityOut)
def create_availability(
    doctor_id: int, data: DoctorAvailabilityCreate, db: Session = Depends(get_db)
):
    if data.doctor_id != doctor_id:
        raise HTTPException(status_code=400, detail="doctor_id mismatch")
    try:
        return AvailabilityService.create_availability(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{doctor_id}/availability", response_model=list[DoctorAvailabilityOut])
def list_availability(doctor_id: int, db: Session = Depends(get_db)):
    try:
        return AvailabilityService.list_availability(db, doctor_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{doctor_id}/time-off", response_model=DoctorTimeOffOut)
def create_time_off(doctor_id: int, data: DoctorTimeOffCreate, db: Session = Depends(get_db)):
    if data.doctor_id != doctor_id:
        raise HTTPException(status_code=400, detail="doctor_id mismatch")
    try:
        return AvailabilityService.create_time_off(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{doctor_id}/available-slots", response_model=list[str])
def suggest_available_slots(
    doctor_id: int,
    from_value: str = Query(..., alias="from"),
    to_value: str = Query(..., alias="to"),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    try:
        return AvailabilityService.suggest_slots(
            db, doctor_id, from_iso=from_value, to_iso=to_value, limit=limit
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
