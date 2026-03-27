from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI(title="API Gateway")

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
TASK_SERVICE_URL = os.getenv("TASK_SERVICE_URL", "http://localhost:8002")


class LoginRequest(BaseModel):
    username: str
    password: str


class TaskRequest(BaseModel):
    title: str
    description: str


@app.get("/")
def root():
    return {"message": "API Gateway is running"}


@app.get("/health")
def health():
    return {"status": "UP", "service": "api_gateway"}


@app.post("/auth/login")
def login(data: LoginRequest):
    response = requests.post(f"{AUTH_SERVICE_URL}/login", json=data.model_dump())
    return response.json()


@app.get("/auth/validate")
def validate(token: str):
    response = requests.get(f"{AUTH_SERVICE_URL}/validate", params={"token": token})
    return response.json()


@app.post("/tasks")
def create_task(data: TaskRequest):
    response = requests.post(f"{TASK_SERVICE_URL}/tasks", json=data.model_dump())
    return response.json()


@app.put("/tasks/{task_id}")
def update_task(task_id: int, data: TaskRequest):
    response = requests.put(
        f"{TASK_SERVICE_URL}/tasks/{task_id}",
        json=data.model_dump()
    )
    return response.json()


@app.get("/tasks")
def get_tasks():
    response = requests.get(f"{TASK_SERVICE_URL}/tasks")
    return response.json()


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    response = requests.delete(f"{TASK_SERVICE_URL}/tasks/{task_id}")
    return response.json()