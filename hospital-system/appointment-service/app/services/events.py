from __future__ import annotations

import json
import logging
from typing import Any

import aio_pika

logger = logging.getLogger(__name__)


async def publish_appointment_created(exchange: aio_pika.Exchange, payload: dict[str, Any]) -> None:
    body = json.dumps(payload, default=str).encode("utf-8")
    message = aio_pika.Message(body=body, delivery_mode=aio_pika.DeliveryMode.PERSISTENT)
    await exchange.publish(message, routing_key="appointment.created")
