from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config.settings import settings
from app.schemas.bodies import (
    AppointmentCreate,
    AvailabilityUpdate,
    DoctorCreate,
    DoctorUpdate,
    LoginRequest,
    PatientCreate,
    PatientUpdate,
    RegisterRequest,
)
from app.services.jwt_service import decode_token_safe
from app.services.proxy import proxy_request
from app.services.rate_limiter import SlidingWindowRateLimiter

logger = logging.getLogger(__name__)
router = APIRouter(tags=["gateway"])

limiter = SlidingWindowRateLimiter(settings.rate_limit_requests, settings.rate_limit_window_seconds)
bearer_scheme = HTTPBearer(auto_error=True)


def rate_guard(request: Request) -> None:
    client = request.client.host if request.client else "unknown"
    if not limiter.allow(client):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")


def bearer_header(credentials: HTTPAuthorizationCredentials) -> str:
    return f"Bearer {credentials.credentials}"


async def jwt_payload(credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]) -> dict:
    try:
        return decode_token_safe(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


def require_roles(*roles: str):
    allowed = set(roles)

    async def _dep(user: Annotated[dict, Depends(jwt_payload)]) -> dict:
        if user.get("role") not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return _dep


@router.post("/auth/register")
async def register(request: Request, body: RegisterRequest):
    rate_guard(request)
    return await proxy_request(
        "POST",
        f"{settings.auth_service_url}/auth/register",
        json_body=body.model_dump(mode="json"),
    )


@router.post("/auth/login")
async def login(request: Request, body: LoginRequest):
    rate_guard(request)
    return await proxy_request(
        "POST",
        f"{settings.auth_service_url}/auth/login",
        json_body=body.model_dump(),
    )


@router.post("/patients")
async def create_patient(
    request: Request,
    body: PatientCreate,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    _: Annotated[dict, Depends(require_roles("admin"))],
):
    rate_guard(request)
    return await proxy_request(
        "POST",
        f"{settings.patient_service_url}/patients",
        authorization=bearer_header(credentials),
        json_body=body.model_dump(mode="json"),
    )


@router.put("/patients/{patient_id}")
async def update_patient(
    request: Request,
    patient_id: int,
    body: PatientUpdate,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    _: Annotated[dict, Depends(require_roles("admin", "patient"))],
):
    rate_guard(request)
    return await proxy_request(
        "PUT",
        f"{settings.patient_service_url}/patients/{patient_id}",
        authorization=bearer_header(credentials),
        json_body=body.model_dump(mode="json", exclude_unset=True, exclude_none=True),
    )


@router.get("/patients/{patient_id}")
async def get_patient(
    request: Request,
    patient_id: int,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    _: Annotated[dict, Depends(require_roles("admin", "doctor", "patient"))],
):
    rate_guard(request)
    return await proxy_request(
        "GET",
        f"{settings.patient_service_url}/patients/{patient_id}",
        authorization=bearer_header(credentials),
    )


@router.get("/patients")
async def list_patients(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    _: Annotated[dict, Depends(require_roles("admin", "doctor"))],
):
    rate_guard(request)
    qs = request.query_params
    url = f"{settings.patient_service_url}/patients"
    if qs:
        url = f"{url}?{qs}"
    return await proxy_request("GET", url, authorization=bearer_header(credentials))


@router.post("/doctors")
async def create_doctor(
    request: Request,
    body: DoctorCreate,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    _: Annotated[dict, Depends(require_roles("admin"))],
):
    rate_guard(request)
    return await proxy_request(
        "POST",
        f"{settings.doctor_service_url}/doctors",
        authorization=bearer_header(credentials),
        json_body=body.model_dump(mode="json"),
    )


@router.put("/doctors/{doctor_id}")
async def update_doctor(
    request: Request,
    doctor_id: int,
    body: DoctorUpdate,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    _: Annotated[dict, Depends(require_roles("admin", "doctor"))],
):
    rate_guard(request)
    return await proxy_request(
        "PUT",
        f"{settings.doctor_service_url}/doctors/{doctor_id}",
        authorization=bearer_header(credentials),
        json_body=body.model_dump(mode="json", exclude_unset=True, exclude_none=True),
    )


@router.put("/doctors/{doctor_id}/availability")
async def set_availability(
    request: Request,
    doctor_id: int,
    body: AvailabilityUpdate,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    _: Annotated[dict, Depends(require_roles("admin", "doctor"))],
):
    rate_guard(request)
    return await proxy_request(
        "PUT",
        f"{settings.doctor_service_url}/doctors/{doctor_id}/availability",
        authorization=bearer_header(credentials),
        json_body=body.model_dump(mode="json"),
    )


@router.get("/doctors/{doctor_id}")
async def get_doctor(
    request: Request,
    doctor_id: int,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    _: Annotated[dict, Depends(require_roles("admin", "doctor", "patient"))],
):
    rate_guard(request)
    return await proxy_request(
        "GET",
        f"{settings.doctor_service_url}/doctors/{doctor_id}",
        authorization=bearer_header(credentials),
    )


@router.get("/doctors")
async def list_doctors(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    _: Annotated[dict, Depends(require_roles("admin", "doctor", "patient"))],
):
    rate_guard(request)
    qs = request.query_params
    url = f"{settings.doctor_service_url}/doctors"
    if qs:
        url = f"{url}?{qs}"
    return await proxy_request("GET", url, authorization=bearer_header(credentials))


@router.post("/appointments")
async def create_appointment(
    request: Request,
    body: AppointmentCreate,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    _: Annotated[dict, Depends(require_roles("admin", "patient"))],
):
    rate_guard(request)
    return await proxy_request(
        "POST",
        f"{settings.appointment_service_url}/appointments",
        authorization=bearer_header(credentials),
        json_body=body.model_dump(mode="json"),
    )


@router.delete("/appointments/{appointment_id}")
async def cancel_appointment(
    request: Request,
    appointment_id: int,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    _: Annotated[dict, Depends(require_roles("admin", "patient", "doctor"))],
):
    rate_guard(request)
    return await proxy_request(
        "DELETE",
        f"{settings.appointment_service_url}/appointments/{appointment_id}",
        authorization=bearer_header(credentials),
    )


@router.get("/appointments")
async def list_appointments(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    _: Annotated[dict, Depends(require_roles("admin", "patient", "doctor"))],
):
    rate_guard(request)
    qs = request.query_params
    url = f"{settings.appointment_service_url}/appointments"
    if qs:
        url = f"{url}?{qs}"
    return await proxy_request("GET", url, authorization=bearer_header(credentials))
