from __future__ import annotations

import logging
from typing import Any

import httpx
from fastapi import HTTPException, Response

from app.config.settings import settings

logger = logging.getLogger(__name__)


def _forward_headers(raw_authorization: str | None) -> dict[str, str]:
    headers: dict[str, str] = {"Accept": "application/json"}
    if raw_authorization:
        headers["Authorization"] = raw_authorization
    return headers


async def proxy_request(
    method: str,
    url: str,
    *,
    authorization: str | None = None,
    json_body: Any | None = None,
    params: dict[str, Any] | None = None,
) -> Response:
    timeout = httpx.Timeout(settings.downstream_timeout_seconds)
    headers = _forward_headers(authorization)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(
                method.upper(),
                url,
                headers=headers,
                json=json_body,
                params=params,
            )
    except httpx.TimeoutException as exc:
        logger.warning("downstream_timeout url=%s", url)
        raise HTTPException(status_code=504, detail="Downstream service timed out") from exc
    except httpx.RequestError as exc:
        logger.warning("downstream_unreachable url=%s error=%s", url, exc)
        raise HTTPException(status_code=503, detail="Downstream service unavailable") from exc

    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type="application/json",
            )
        except Exception:  # noqa: BLE001
            pass

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type=content_type or "text/plain",
    )
