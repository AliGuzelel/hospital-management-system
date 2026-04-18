import asyncio
import aio_pika
from app.config.settings import settings
from app.config.logging import setup_logging

logger = setup_logging(settings.service_name)

async def _consume():
    conn = await aio_pika.connect_robust(settings.rabbitmq_url)
    ch = await conn.channel()
    ex = await ch.declare_exchange("hospital.events", aio_pika.ExchangeType.TOPIC, durable=True)
    q = await ch.declare_queue("notification.queue", durable=True)
    await q.bind(ex, routing_key="appointment.*")
    async with q.iterator() as it:
        async for message in it:
            async with message.process():
                logger.info("notification_event", extra={"payload": message.body.decode()})

def start_consumer_background():
    return asyncio.create_task(_consume())
