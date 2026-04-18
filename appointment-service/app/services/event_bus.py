import asyncio
import json
import aio_pika
from app.config.settings import settings

async def _publish(event_type: str, payload: dict):
    conn = await aio_pika.connect_robust(settings.rabbitmq_url)
    async with conn:
        ch = await conn.channel()
        ex = await ch.declare_exchange("hospital.events", aio_pika.ExchangeType.TOPIC, durable=True)
        await ex.publish(aio_pika.Message(body=json.dumps(payload).encode()), routing_key=event_type)

def publish_event_sync(event_type: str, payload: dict):
    asyncio.run(_publish(event_type, payload))
