"""
API Gateway entrypoint.

From this folder (`gateway/`):
  uvicorn main:app --host 0.0.0.0 --port 8000

From repo root (`distributed-task-system/`), use the root `main.py` shim the same way:
  uvicorn main:app --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from routes.appointments import router as appointments_router
from routes.auth import router as auth_router
from routes.doctors import router as doctors_router
from routes.patients import router as patients_router

app = FastAPI(title="API Gateway")


@app.get("/", response_class=PlainTextResponse)
def root():
    return "API Gateway Running"


@app.get("/health")
def health():
    return {"status": "healthy", "service": "api-gateway"}


app.include_router(auth_router)
app.include_router(patients_router)
app.include_router(doctors_router)
app.include_router(appointments_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
