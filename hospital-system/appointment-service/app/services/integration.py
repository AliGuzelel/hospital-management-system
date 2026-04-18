from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class IntegrationError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


async def get_patient_internal(
    client: httpx.AsyncClient,
    base_url: str,
    patient_id: int,
    service_token: str,
) -> dict[str, Any]:
    url = f"{base_url.rstrip('/')}/internal/patients/{patient_id}"
    headers = {"X-Service-Token": service_token}
    try:
        response = await client.get(url, headers=headers)
    except httpx.RequestError as exc:
        logger.warning("patient_service_unreachable error=%s", exc)
        raise IntegrationError(503, "Patient service unavailable") from exc

    if response.status_code == 404:
        raise LookupError("Patient not found")
    if response.status_code >= 400:
        raise IntegrationError(response.status_code, response.text)
    return response.json()


async def get_doctor_internal(
    client: httpx.AsyncClient,
    base_url: str,
    doctor_id: int,
    service_token: str,
) -> dict[str, Any]:
    url = f"{base_url.rstrip('/')}/internal/doctors/{doctor_id}"
    headers = {"X-Service-Token": service_token}
    try:
        response = await client.get(url, headers=headers)
    except httpx.RequestError as exc:
        logger.warning("doctor_service_unreachable error=%s", exc)
        raise IntegrationError(503, "Doctor service unavailable") from exc

    if response.status_code == 404:
        raise LookupError("Doctor not found")
    if response.status_code >= 400:
        raise IntegrationError(response.status_code, response.text)
    return response.json()
