import logging
from contextlib import asynccontextmanager

import aio_pika
import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text

from app.config.settings import settings
from app.database.session import engine
from app.models.appointment import Base
from app.routes.appointment_routes import router as appointment_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        if settings.database_url.startswith("sqlite"):
            await conn.execute(text("PRAGMA journal_mode=WAL"))

    app.state.http = httpx.AsyncClient(timeout=10.0)
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    exchange = await channel.declare_exchange(
        settings.rabbitmq_exchange,
        aio_pika.ExchangeType.TOPIC,
        durable=True,
    )
    app.state.rabbit = {"connection": connection, "channel": channel, "exchange": exchange}

    yield

    await app.state.http.aclose()
    await connection.close()


app = FastAPI(title="Appointment Service", lifespan=lifespan)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):  # noqa: ANN001
    logger.exception("unhandled_error path=%s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
async def health():
    return {"status": "UP", "service": settings.service_name}


app.include_router(appointment_router)
Instrumentator().instrument(app).expose(app)
