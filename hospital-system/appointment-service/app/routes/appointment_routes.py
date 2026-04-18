import logging

import httpx
from aio_pika import Exchange
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.schemas.appointment import AppointmentCreate, AppointmentOut
from app.services import integration
from app.services.appointment_service import AppointmentService
from app.utils.deps import require_roles

logger = logging.getLogger(__name__)
router = APIRouter(tags=["appointments"])


def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http


def get_exchange(request: Request) -> Exchange:
    return request.app.state.rabbit["exchange"]


@router.post("/appointments", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    payload: AppointmentCreate,
    user: dict = Depends(require_roles("admin", "patient")),
    db: AsyncSession = Depends(get_session),
    http: httpx.AsyncClient = Depends(get_http_client),
    exchange: Exchange = Depends(get_exchange),
):
    booked_by = int(user["sub"])
    try:
        appt = await AppointmentService.create(db, http, exchange, payload, booked_by)
    except integration.IntegrationError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return appt


@router.delete("/appointments/{appointment_id}", response_model=AppointmentOut)
async def cancel_appointment(
    appointment_id: int,
    user: dict = Depends(require_roles("admin", "patient", "doctor")),
    db: AsyncSession = Depends(get_session),
    http: httpx.AsyncClient = Depends(get_http_client),
):
    try:
        appt = await AppointmentService.cancel(db, http, appointment_id, user)
    except integration.IntegrationError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return appt


@router.get("/appointments", response_model=list[AppointmentOut])
async def list_appointments(
    user: dict = Depends(require_roles("admin", "patient", "doctor")),
    db: AsyncSession = Depends(get_session),
    http: httpx.AsyncClient = Depends(get_http_client),
    patient_id: int | None = Query(default=None),
    doctor_id: int | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    try:
        return await AppointmentService.list_appointments(
            db, http, user, patient_id, doctor_id, limit, offset
        )
    except integration.IntegrationError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
