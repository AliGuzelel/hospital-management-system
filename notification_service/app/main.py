from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Notification Service")


class NotificationRequest(BaseModel):
    message: str = Field(..., min_length=1)


@app.get("/")
def root():
    return {"message": "Notification Service is running"}


@app.get("/health")
def health():
    return {"status": "UP", "service": "notification_service"}


@app.post("/notify")
def send_notification(data: NotificationRequest):
    return {
        "status": "sent",
        "message": data.message
    }