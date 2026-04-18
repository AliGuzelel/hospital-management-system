from contextlib import asynccontextmanager
from app.main_base import app
from app.services.consumer import start_consumer_background

@asynccontextmanager
async def lifespan(_: object):
    task = start_consumer_background()
    try:
        yield
    finally:
        task.cancel()

app.router.lifespan_context = lifespan
