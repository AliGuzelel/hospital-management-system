from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config.settings import settings
from app.config.rate_limiter import InMemoryRateLimiter
from app.schemas.bodies import (
    AppointmentCreateBody,
    DoctorCreateBody,
    DoctorUpdateBody,
    LoginBody,
    PatientCreateBody,
    PatientUpdateBody,
    RegisterBody,
)
from app.services.auth_service import GatewayAuthService
from app.services.proxy_service import ProxyService

router = APIRouter(tags=["gateway"])
limiter = InMemoryRateLimiter(settings.rate_limit_requests, settings.rate_limit_window_seconds)
bearer_scheme = HTTPBearer()


def rate_guard(request: Request):
    key = request.client.host if request.client else "unknown"
    if not limiter.allow(key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")


def auth_guard(credentials: HTTPAuthorizationCredentials, roles: set[str]):
    try:
        payload = GatewayAuthService.decode_token(credentials.credentials)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token") from None
    if payload.get("role") not in roles:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/auth/register")
async def register(request: Request, body: RegisterBody):
    rate_guard(request)
    return await ProxyService.forward(
        "POST", f"{settings.auth_service_url}/auth/register", body.model_dump()
    )


@router.post("/auth/login")
async def login(request: Request, body: LoginBody):
    rate_guard(request)
    return await ProxyService.forward(
        "POST", f"{settings.auth_service_url}/auth/login", body.model_dump()
    )


@router.post("/patients")
async def create_patient(
    request: Request,
    body: PatientCreateBody,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    rate_guard(request)
    auth_guard(credentials, {"admin"})
    return await ProxyService.forward(
        "POST", f"{settings.patient_service_url}/patients", body.model_dump()
    )


@router.get("/patients/{patient_id}")
async def get_patient(
    patient_id: int,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    rate_guard(request)
    auth_guard(credentials, {"admin", "doctor", "patient"})
    return await ProxyService.forward("GET", f"{settings.patient_service_url}/patients/{patient_id}")


@router.put("/patients/{patient_id}")
async def update_patient(
    patient_id: int,
    request: Request,
    body: PatientUpdateBody,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    rate_guard(request)
    auth_guard(credentials, {"admin", "patient"})
    payload = body.model_dump(exclude_unset=True, exclude_none=True)
    return await ProxyService.forward(
        "PUT", f"{settings.patient_service_url}/patients/{patient_id}", payload
    )


@router.post("/doctors")
async def create_doctor(
    request: Request,
    body: DoctorCreateBody,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    rate_guard(request)
    auth_guard(credentials, {"admin"})
    return await ProxyService.forward(
        "POST", f"{settings.doctor_service_url}/doctors", body.model_dump()
    )


@router.get("/doctors/{doctor_id}/appointments")
async def list_doctor_appointments(
    doctor_id: int,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    appointment_filter: Optional[str] = Query(default=None, alias="type"),
):
    rate_guard(request)
    auth_guard(credentials, {"admin", "doctor"})
    params = {"type": appointment_filter} if appointment_filter else None
    return await ProxyService.forward(
        "GET",
        f"{settings.appointment_service_url}/doctors/{doctor_id}/appointments",
        params=params,
    )


@router.get("/doctors/{doctor_id}")
async def get_doctor(
    doctor_id: int,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    rate_guard(request)
    auth_guard(credentials, {"admin", "doctor", "patient"})
    return await ProxyService.forward("GET", f"{settings.doctor_service_url}/doctors/{doctor_id}")


@router.put("/doctors/{doctor_id}")
async def update_doctor(
    doctor_id: int,
    request: Request,
    body: DoctorUpdateBody,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    rate_guard(request)
    auth_guard(credentials, {"admin", "doctor"})
    payload = body.model_dump(exclude_unset=True, exclude_none=True)
    return await ProxyService.forward(
        "PUT", f"{settings.doctor_service_url}/doctors/{doctor_id}", payload
    )


@router.post("/appointments")
async def create_appointment(
    request: Request,
    body: AppointmentCreateBody,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    rate_guard(request)
    auth_guard(credentials, {"admin", "patient"})
    return await ProxyService.forward(
        "POST", f"{settings.appointment_service_url}/appointments", body.model_dump()
    )


@router.delete("/appointments/{appointment_id}")
async def cancel_appointment(
    appointment_id: int,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    rate_guard(request)
    auth_guard(credentials, {"admin", "patient"})
    return await ProxyService.forward(
        "DELETE", f"{settings.appointment_service_url}/appointments/{appointment_id}"
    )


@router.post("/appointments/{appointment_id}/complete")
async def complete_appointment(
    appointment_id: int,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    rate_guard(request)
    auth_guard(credentials, {"admin", "doctor"})
    return await ProxyService.forward(
        "POST", f"{settings.appointment_service_url}/appointments/{appointment_id}/complete"
    )


@router.get("/invoices")
async def list_invoices(
    request: Request,
    patient_id: int | None = Query(default=None),
    doctor_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    rate_guard(request)
    auth_guard(credentials, {"admin", "doctor", "patient"})
    params = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "status": status,
    }
    filtered = {k: v for k, v in params.items() if v is not None}
    return await ProxyService.forward(
        "GET", f"{settings.appointment_service_url}/invoices", params=filtered or None
    )


@router.get("/invoices/{invoice_id}")
async def get_invoice(
    invoice_id: int,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    rate_guard(request)
    auth_guard(credentials, {"admin", "doctor", "patient"})
    return await ProxyService.forward(
        "GET", f"{settings.appointment_service_url}/invoices/{invoice_id}"
    )


@router.patch("/invoices/{invoice_id}/mark-paid")
async def mark_invoice_paid(
    invoice_id: int,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    rate_guard(request)
    auth_guard(credentials, {"admin"})
    return await ProxyService.forward(
        "PATCH", f"{settings.appointment_service_url}/invoices/{invoice_id}/mark-paid"
    )


@router.get("/notifications/{user_id}")
async def list_notifications(
    user_id: int,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    rate_guard(request)
    auth_guard(credentials, {"admin", "doctor", "patient"})
    return await ProxyService.forward(
        "GET", f"{settings.appointment_service_url}/notifications/{user_id}"
    )


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    rate_guard(request)
    auth_guard(credentials, {"admin", "doctor", "patient"})
    return await ProxyService.forward(
        "PUT", f"{settings.appointment_service_url}/notifications/{notification_id}/read"
    )
