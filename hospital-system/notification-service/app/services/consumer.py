import json
import logging

import aio_pika

logger = logging.getLogger(__name__)


async def handle_message(message: aio_pika.IncomingMessage) -> None:
    async with message.process(requeue=False):
        try:
            payload = json.loads(message.body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            logger.warning("notification_invalid_json")
            return

        event = payload.get("event")
        if event == "appointment_created":
            logger.info(
                "appointment_notification appointment_id=%s patient_id=%s doctor_id=%s",
                payload.get("appointment_id"),
                payload.get("patient_id"),
                payload.get("doctor_id"),
            )
        else:
            logger.info("notification_event event=%s payload=%s", event, payload)
