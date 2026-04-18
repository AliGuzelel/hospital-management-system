import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.schemas.patient import InternalPatientOut, PatientCreate, PatientOut, PatientUpdate
from app.services.patient_service import PatientService
from app.utils.deps import require_roles, verify_internal_token

logger = logging.getLogger(__name__)
router = APIRouter(tags=["patients"])


@router.post("/patients", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
async def create_patient(
    payload: PatientCreate,
    _: dict = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_session),
):
    try:
        patient = await PatientService.create(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    logger.info("patient_created", extra={"patient_id": patient.id})
    return patient


@router.put("/patients/{patient_id}", response_model=PatientOut)
async def update_patient(
    patient_id: int,
    payload: PatientUpdate,
    user: dict = Depends(require_roles("admin", "patient")),
    db: AsyncSession = Depends(get_session),
):
    if user.get("role") == "patient":
        existing = await PatientService.get(db, patient_id)
        if existing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
        if existing.user_id is None or int(user.get("sub", 0)) != int(existing.user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update this patient")

    try:
        patient = await PatientService.update(db, patient_id, payload)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return patient


@router.get("/patients/{patient_id}", response_model=PatientOut)
async def get_patient(
    patient_id: int,
    user: dict = Depends(require_roles("admin", "doctor", "patient")),
    db: AsyncSession = Depends(get_session),
):
    patient = await PatientService.get(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    if user.get("role") == "patient":
        if patient.user_id is None or int(user.get("sub", 0)) != int(patient.user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view this patient")

    return patient


@router.get("/patients", response_model=list[PatientOut])
async def list_patients(
    _: dict = Depends(require_roles("admin", "doctor")),
    db: AsyncSession = Depends(get_session),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    return await PatientService.list_patients(db, limit=limit, offset=offset)


@router.get("/internal/patients/{patient_id}", response_model=InternalPatientOut)
async def internal_get_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_session),
    _: None = Depends(verify_internal_token),
):
    patient = await PatientService.get(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return InternalPatientOut(
        id=patient.id,
        name=patient.name,
        email=patient.email,
        user_id=patient.user_id,
    )
