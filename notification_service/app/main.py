from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Notification Service")


class NotificationRequest(BaseModel):
    message: str


@app.get("/")
def root():
    return {"message": "Notification Service is running"}


@app.post("/notify")
def send_notification(data: NotificationRequest):
    return {
        "status": "sent",
        "message": data.message
    }