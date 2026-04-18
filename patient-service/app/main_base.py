from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from app.config.settings import settings

app = FastAPI(title="Patient Service")

@app.get("/")
def root():
    return {"service": settings.service_name, "status": "running"}

@app.get("/health")
def health():
    return {"status": "UP", "service": settings.service_name}

Instrumentator().instrument(app).expose(app)
