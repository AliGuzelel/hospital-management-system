import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.schemas.doctor import AvailabilityUpdate, DoctorCreate, DoctorOut, DoctorUpdate
from app.services.doctor_service import DoctorService
from app.utils.deps import require_roles, verify_internal_token

logger = logging.getLogger(__name__)
router = APIRouter(tags=["doctors"])


@router.post("/doctors", response_model=DoctorOut, status_code=status.HTTP_201_CREATED)
async def create_doctor(
    payload: DoctorCreate,
    _: dict = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_session),
):
    try:
        doctor = await DoctorService.create(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    logger.info("doctor_created", extra={"doctor_id": doctor.id})
    return DoctorService.to_out(doctor)


@router.put("/doctors/{doctor_id}", response_model=DoctorOut)
async def update_doctor(
    doctor_id: int,
    payload: DoctorUpdate,
    user: dict = Depends(require_roles("admin", "doctor")),
    db: AsyncSession = Depends(get_session),
):
    if user.get("role") == "doctor":
        existing = await DoctorService.get(db, doctor_id)
        if existing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
        if existing.user_id is None or int(user.get("sub", 0)) != int(existing.user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update this doctor")

    try:
        doctor = await DoctorService.update(db, doctor_id, payload)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return DoctorService.to_out(doctor)


@router.put("/doctors/{doctor_id}/availability", response_model=DoctorOut)
async def set_availability(
    doctor_id: int,
    payload: AvailabilityUpdate,
    user: dict = Depends(require_roles("admin", "doctor")),
    db: AsyncSession = Depends(get_session),
):
    if user.get("role") == "doctor":
        existing = await DoctorService.get(db, doctor_id)
        if existing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
        if existing.user_id is None or int(user.get("sub", 0)) != int(existing.user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update this doctor")

    try:
        doctor = await DoctorService.set_availability(db, doctor_id, payload)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return DoctorService.to_out(doctor)


@router.get("/doctors/{doctor_id}", response_model=DoctorOut)
async def get_doctor(
    doctor_id: int,
    _: dict = Depends(require_roles("admin", "doctor", "patient")),
    db: AsyncSession = Depends(get_session),
):
    doctor = await DoctorService.get(db, doctor_id)
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    return DoctorService.to_out(doctor)


@router.get("/doctors", response_model=list[DoctorOut])
async def list_doctors(
    _: dict = Depends(require_roles("admin", "doctor", "patient")),
    db: AsyncSession = Depends(get_session),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    doctors = await DoctorService.list_doctors(db, limit=limit, offset=offset)
    return [DoctorService.to_out(d) for d in doctors]


@router.get("/internal/doctors/{doctor_id}", response_model=DoctorOut)
async def internal_get_doctor(
    doctor_id: int,
    db: AsyncSession = Depends(get_session),
    _: None = Depends(verify_internal_token),
):
    doctor = await DoctorService.get(db, doctor_id)
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    return DoctorService.to_out(doctor)
