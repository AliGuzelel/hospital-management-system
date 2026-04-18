import logging
from contextlib import asynccontextmanager
from typing import Any

import aio_pika
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.config.settings import settings
from app.services.consumer import handle_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)

    exchange = await channel.declare_exchange(
        settings.rabbitmq_exchange,
        aio_pika.ExchangeType.TOPIC,
        durable=True,
    )
    queue = await channel.declare_queue("notification-service", durable=True)
    await queue.bind(exchange, routing_key="appointment.created")

    consumer_tag = await queue.consume(handle_message)
    app.state.rabbit = {"connection": connection, "consumer_tag": consumer_tag, "queue": queue}

    try:
        yield
    finally:
        rabbit: dict[str, Any] = app.state.rabbit
        await rabbit["queue"].cancel(rabbit["consumer_tag"])
        await rabbit["connection"].close()


app = FastAPI(title="Notification Service", lifespan=lifespan)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):  # noqa: ANN001
    logger.exception("unhandled_error path=%s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
async def health():
    return {"status": "UP", "service": settings.service_name}


Instrumentator().instrument(app).expose(app)
