from pathlib import Path


root = Path(".")


def write(path: str, content: str) -> None:
    p = root / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + "\n", encoding="utf-8")


service_names = [
    ("api-gateway", 8000),
    ("auth-service", 8001),
    ("patient-service", 8002),
    ("doctor-service", 8003),
    ("appointment-service", 8004),
    ("notification-service", 8005),
]

for name, _ in service_names:
    for folder in ["routes", "services", "models", "schemas", "database", "config"]:
        write(f"{name}/app/{folder}/__init__.py", "")
    write(f"{name}/app/__init__.py", "")
    write(f"{name}/tests/.gitkeep", "")

write(
    ".env",
    """
JWT_SECRET=super-secret-change-me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
AUTH_SERVICE_URL=http://auth-service:8001
PATIENT_SERVICE_URL=http://patient-service:8002
DOCTOR_SERVICE_URL=http://doctor-service:8003
APPOINTMENT_SERVICE_URL=http://appointment-service:8004
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60
""",
)

write(
    "prometheus.yml",
    """
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: api-gateway
    static_configs:
      - targets: ["api-gateway:8000"]
  - job_name: auth-service
    static_configs:
      - targets: ["auth-service:8001"]
  - job_name: patient-service
    static_configs:
      - targets: ["patient-service:8002"]
  - job_name: doctor-service
    static_configs:
      - targets: ["doctor-service:8003"]
  - job_name: appointment-service
    static_configs:
      - targets: ["appointment-service:8004"]
  - job_name: notification-service
    static_configs:
      - targets: ["notification-service:8005"]
""",
)

write(
    "docker-compose.yml",
    """
services:
  api-gateway:
    build: ./api-gateway
    ports: ["8000:8000"]
    env_file: .env
    depends_on:
      auth-service: {condition: service_healthy}
      patient-service: {condition: service_healthy}
      doctor-service: {condition: service_healthy}
      appointment-service: {condition: service_healthy}
  auth-service:
    build: ./auth-service
    ports: ["8001:8001"]
    env_file: .env
  patient-service:
    build: ./patient-service
    ports: ["8002:8002"]
    env_file: .env
  doctor-service:
    build: ./doctor-service
    ports: ["8003:8003"]
    env_file: .env
  appointment-service:
    build: ./appointment-service
    ports: ["8004:8004"]
    env_file: .env
    depends_on:
      rabbitmq: {condition: service_healthy}
      patient-service: {condition: service_healthy}
      doctor-service: {condition: service_healthy}
  notification-service:
    build: ./notification-service
    ports: ["8005:8005"]
    env_file: .env
    depends_on:
      rabbitmq: {condition: service_healthy}

  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "check_port_connectivity"]
      interval: 10s
      timeout: 5s
      retries: 10

  prometheus:
    image: prom/prometheus:latest
    ports: ["9090:9090"]
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro

  grafana:
    image: grafana/grafana:latest
    ports: ["3000:3000"]
""",
)

base_req = """fastapi==0.115.5
uvicorn==0.32.1
pydantic==2.10.2
pydantic-settings==2.6.1
sqlalchemy==2.0.36
httpx==0.27.2
prometheus-fastapi-instrumentator==7.0.2
python-json-logger==2.0.7
pytest==8.3.3
email-validator==2.3.0
"""

for service, port in service_names:
    write(
        f"{service}/Dockerfile",
        f"""
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
EXPOSE {port}
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "{port}"]
""",
    )

write("patient-service/requirements.txt", base_req)
write("doctor-service/requirements.txt", base_req)
write("api-gateway/requirements.txt", base_req + "python-jose[cryptography]==3.3.0\n")
write(
    "auth-service/requirements.txt",
    base_req + "python-jose[cryptography]==3.3.0\npasslib[bcrypt]==1.7.4\n",
)
write("appointment-service/requirements.txt", base_req + "aio-pika==9.5.0\n")
write("notification-service/requirements.txt", base_req + "aio-pika==9.5.0\n")

shared_logging = """
import logging
from pythonjsonlogger import jsonlogger

def setup_logging(service_name: str) -> logging.Logger:
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(jsonlogger.JsonFormatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
    return logger
"""

shared_session = """
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./hospital.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""

shared_base_main = """
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from app.config.settings import settings

app = FastAPI(title="{title}")

@app.get("/")
def root():
    return {{"service": settings.service_name, "status": "running"}}

@app.get("/health")
def health():
    return {{"status": "UP", "service": settings.service_name}}

Instrumentator().instrument(app).expose(app)
"""

# Auth
write(
    "auth-service/app/config/settings.py",
    """
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    service_name: str = "auth-service"
    jwt_secret: str = "super-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
""",
)
write("auth-service/app/config/logging.py", shared_logging)
write("auth-service/app/database/session.py", shared_session)
write(
    "auth-service/app/models/user.py",
    """
from sqlalchemy import Column, Integer, String
from app.database.session import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False)
""",
)
write(
    "auth-service/app/schemas/auth.py",
    """
from pydantic import BaseModel, Field

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    role: str

class LoginRequest(BaseModel):
    username: str
    password: str
""",
)
write(
    "auth-service/app/services/auth_service.py",
    """
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.config.settings import settings
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ROLES = {"admin", "doctor", "patient"}

class AuthService:
    @staticmethod
    def register(db: Session, username: str, password: str, role: str):
        if role not in ROLES:
            raise ValueError("Invalid role")
        if db.query(User).filter(User.username == username).first():
            raise ValueError("Username already exists")
        user = User(username=username, hashed_password=pwd_context.hash(password), role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def login(db: Session, username: str, password: str):
        user = db.query(User).filter(User.username == username).first()
        if not user or not pwd_context.verify(password, user.hashed_password):
            raise ValueError("Invalid credentials")
        exp = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
        token = jwt.encode({"sub": user.username, "role": user.role, "exp": exp}, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        return token, user.role

    @staticmethod
    def validate(token: str):
        try:
            return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        except JWTError as exc:
            raise ValueError("Invalid token") from exc
""",
)
write(
    "auth-service/app/routes/auth_routes.py",
    """
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.auth import RegisterRequest, LoginRequest
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = AuthService.register(db, data.username, data.password, data.role)
        return {"id": user.id, "username": user.username, "role": user.role}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    try:
        token, role = AuthService.login(db, data.username, data.password)
        return {"access_token": token, "token_type": "bearer", "role": role}
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

@router.get("/validate")
def validate(token: str):
    try:
        payload = AuthService.validate(token)
        return {"valid": True, "username": payload["sub"], "role": payload["role"]}
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
""",
)
write("auth-service/app/main_base.py", shared_base_main.format(title="Auth Service"))
write(
    "auth-service/app/main.py",
    """
from app.database.session import Base, engine
from app.main_base import app
from app.routes.auth_routes import router

Base.metadata.create_all(bind=engine)
app.include_router(router)
""",
)
write(
    "auth-service/tests/test_auth.py",
    """
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_auth_flow():
    client.post("/auth/register", json={"username": "u1", "password": "secret12", "role": "patient"})
    login = client.post("/auth/login", json={"username": "u1", "password": "secret12"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    check = client.get("/auth/validate", params={"token": token})
    assert check.status_code == 200
""",
)

# Patient and Doctor
for svc, title, model, route, extra_model, extra_field in [
    ("patient-service", "Patient Service", "Patient", "patients", "", ""),
    ("doctor-service", "Doctor Service", "Doctor", "doctors", "availability = Column(String(255), nullable=True)", "availability: str | None = None"),
]:
    write(
        f"{svc}/app/config/settings.py",
        f"""
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    service_name: str = "{svc}"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
settings = Settings()
""",
    )
    write(f"{svc}/app/config/logging.py", shared_logging)
    write(f"{svc}/app/database/session.py", shared_session)
    write(
        f"{svc}/app/models/{model.lower()}.py",
        f"""
from sqlalchemy import Column, Integer, String
from app.database.session import Base

class {model}(Base):
    __tablename__ = "{route}"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), nullable=False, unique=True)
    phone = Column(String(30), nullable=False)
    {extra_model}
""",
    )
    write(
        f"{svc}/app/schemas/{model.lower()}.py",
        f"""
from pydantic import BaseModel, EmailStr
class {model}Create(BaseModel):
    name: str
    email: EmailStr
    phone: str
    {extra_field}
class {model}Update(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    {extra_field}
class {model}Out(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    {extra_field}
    class Config:
        from_attributes = True
""",
    )
    write(
        f"{svc}/app/services/{model.lower()}_service.py",
        f"""
from sqlalchemy.orm import Session
from app.models.{model.lower()} import {model}

class {model}Service:
    @staticmethod
    def create(db: Session, data):
        obj = {model}(**data.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    @staticmethod
    def get(db: Session, item_id: int):
        return db.query({model}).filter({model}.id == item_id).first()
    @staticmethod
    def update(db: Session, item_id: int, data):
        obj = db.query({model}).filter({model}.id == item_id).first()
        if not obj:
            return None
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
        return obj
""",
    )
    write(
        f"{svc}/app/routes/{route}_routes.py",
        f"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.{model.lower()} import {model}Create, {model}Update, {model}Out
from app.services.{model.lower()}_service import {model}Service

router = APIRouter(prefix="/{route}", tags=["{route}"])

@router.post("", response_model={model}Out)
def create_item(data: {model}Create, db: Session = Depends(get_db)):
    return {model}Service.create(db, data)

@router.get("/{{item_id}}", response_model={model}Out)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = {model}Service.get(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item

@router.put("/{{item_id}}", response_model={model}Out)
def update_item(item_id: int, data: {model}Update, db: Session = Depends(get_db)):
    item = {model}Service.update(db, item_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item
""",
    )
    write(f"{svc}/app/main_base.py", shared_base_main.format(title=title))
    write(
        f"{svc}/app/main.py",
        f"""
from app.database.session import Base, engine
from app.main_base import app
from app.routes.{route}_routes import router
Base.metadata.create_all(bind=engine)
app.include_router(router)
""",
    )
    write(
        f"{svc}/tests/test_{route}.py",
        f"""
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
def test_create_and_get():
    payload = {{"name":"n1","email":"n1@example.com","phone":"111"{', "availability":"Mon-Fri"' if svc == 'doctor-service' else ''}}}
    created = client.post("/{route}", json=payload)
    assert created.status_code == 200
    fetched = client.get(f"/{route}/{{created.json()['id']}}")
    assert fetched.status_code == 200
""",
    )

# Appointment
write(
    "appointment-service/app/config/settings.py",
    """
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    service_name: str = "appointment-service"
    patient_service_url: str = "http://patient-service:8002"
    doctor_service_url: str = "http://doctor-service:8003"
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
settings = Settings()
""",
)
write("appointment-service/app/config/logging.py", shared_logging)
write("appointment-service/app/database/session.py", shared_session)
write(
    "appointment-service/app/models/appointment.py",
    """
from sqlalchemy import Column, Integer, String
from app.database.session import Base
class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    doctor_id = Column(Integer, nullable=False)
    date_time = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="booked")
""",
)
write(
    "appointment-service/app/schemas/appointment.py",
    """
from pydantic import BaseModel
class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    date_time: str
class AppointmentOut(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    date_time: str
    status: str
    class Config:
        from_attributes = True
""",
)
write(
    "appointment-service/app/services/event_bus.py",
    """
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
""",
)
write(
    "appointment-service/app/services/appointment_service.py",
    """
import httpx
from sqlalchemy.orm import Session
from app.config.settings import settings
from app.models.appointment import Appointment
from app.services.event_bus import publish_event_sync

class AppointmentService:
    @staticmethod
    def _validate_entities(patient_id: int, doctor_id: int):
        p = httpx.get(f"{settings.patient_service_url}/patients/{patient_id}", timeout=5)
        d = httpx.get(f"{settings.doctor_service_url}/doctors/{doctor_id}", timeout=5)
        if p.status_code != 200:
            raise ValueError("Invalid patient")
        if d.status_code != 200:
            raise ValueError("Invalid doctor")
    @staticmethod
    def book(db: Session, data):
        AppointmentService._validate_entities(data.patient_id, data.doctor_id)
        obj = Appointment(patient_id=data.patient_id, doctor_id=data.doctor_id, date_time=data.date_time, status="booked")
        db.add(obj)
        db.commit()
        db.refresh(obj)
        publish_event_sync("appointment.created", {"appointment_id": obj.id, "patient_id": obj.patient_id, "doctor_id": obj.doctor_id})
        return obj
    @staticmethod
    def cancel(db: Session, appointment_id: int):
        obj = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not obj:
            return None
        obj.status = "cancelled"
        db.commit()
        db.refresh(obj)
        publish_event_sync("appointment.cancelled", {"appointment_id": obj.id})
        return obj
""",
)
write(
    "appointment-service/app/routes/appointment_routes.py",
    """
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.appointment import AppointmentCreate, AppointmentOut
from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.post("", response_model=AppointmentOut)
def book(data: AppointmentCreate, db: Session = Depends(get_db)):
    try:
        return AppointmentService.book(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@router.delete("/{appointment_id}", response_model=AppointmentOut)
def cancel(appointment_id: int, db: Session = Depends(get_db)):
    result = AppointmentService.cancel(db, appointment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return result
""",
)
write("appointment-service/app/main_base.py", shared_base_main.format(title="Appointment Service"))
write(
    "appointment-service/app/main.py",
    """
from app.database.session import Base, engine
from app.main_base import app
from app.routes.appointment_routes import router
Base.metadata.create_all(bind=engine)
app.include_router(router)
""",
)
write(
    "appointment-service/tests/test_appointments.py",
    """
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

@patch("app.services.appointment_service.httpx.get")
@patch("app.services.appointment_service.publish_event_sync")
def test_book_cancel(mock_publish, mock_get):
    mock_get.return_value.status_code = 200
    book = client.post("/appointments", json={"patient_id":1,"doctor_id":1,"date_time":"2026-04-01T10:00:00Z"})
    assert book.status_code == 200
    cancel = client.delete(f"/appointments/{book.json()['id']}")
    assert cancel.status_code == 200
""",
)

# Notification
write(
    "notification-service/app/config/settings.py",
    """
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    service_name: str = "notification-service"
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
settings = Settings()
""",
)
write("notification-service/app/config/logging.py", shared_logging)
write("notification-service/app/database/session.py", shared_session)
write(
    "notification-service/app/services/consumer.py",
    """
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
""",
)
write("notification-service/app/main_base.py", shared_base_main.format(title="Notification Service"))
write(
    "notification-service/app/main.py",
    """
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
""",
)
write(
    "notification-service/tests/test_notification.py",
    """
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
def test_health():
    res = client.get("/health")
    assert res.status_code == 200
""",
)

# API gateway
write(
    "api-gateway/app/config/settings.py",
    """
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    service_name: str = "api-gateway"
    auth_service_url: str = "http://auth-service:8001"
    patient_service_url: str = "http://patient-service:8002"
    doctor_service_url: str = "http://doctor-service:8003"
    appointment_service_url: str = "http://appointment-service:8004"
    jwt_secret: str = "super-secret-change-me"
    jwt_algorithm: str = "HS256"
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
settings = Settings()
""",
)
write("api-gateway/app/config/logging.py", shared_logging)
write(
    "api-gateway/app/config/rate_limiter.py",
    """
import time
from collections import defaultdict, deque
class InMemoryRateLimiter:
    def __init__(self, limit: int, window: int):
        self.limit = limit
        self.window = window
        self.requests = defaultdict(deque)
    def allow(self, key: str) -> bool:
        now = time.time()
        q = self.requests[key]
        while q and q[0] < now - self.window:
            q.popleft()
        if len(q) >= self.limit:
            return False
        q.append(now)
        return True
""",
)
write(
    "api-gateway/app/services/auth_service.py",
    """
from jose import JWTError, jwt
from app.config.settings import settings
class GatewayAuthService:
    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        except JWTError as exc:
            raise ValueError("Invalid token") from exc
""",
)
write(
    "api-gateway/app/services/proxy_service.py",
    """
import httpx
from fastapi import HTTPException
class ProxyService:
    @staticmethod
    async def forward(method: str, url: str, body=None):
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.request(method, url, json=body)
            if res.status_code >= 400:
                raise HTTPException(status_code=res.status_code, detail=res.text)
            return res.json()
""",
)
write(
    "api-gateway/app/routes/gateway_routes.py",
    """
from fastapi import APIRouter, HTTPException, Request
from app.config.settings import settings
from app.config.rate_limiter import InMemoryRateLimiter
from app.services.auth_service import GatewayAuthService
from app.services.proxy_service import ProxyService

router = APIRouter(tags=["gateway"])
limiter = InMemoryRateLimiter(settings.rate_limit_requests, settings.rate_limit_window_seconds)

def rate_guard(request: Request):
    key = request.client.host if request.client else "unknown"
    if not limiter.allow(key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

def auth_guard(request: Request, roles: set[str]):
    hdr = request.headers.get("Authorization")
    if not hdr or not hdr.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    payload = GatewayAuthService.decode_token(hdr.split(" ", 1)[1])
    if payload.get("role") not in roles:
        raise HTTPException(status_code=403, detail="Forbidden")

@router.post("/auth/register")
async def register(request: Request):
    rate_guard(request)
    return await ProxyService.forward("POST", f"{settings.auth_service_url}/auth/register", await request.json())

@router.post("/auth/login")
async def login(request: Request):
    rate_guard(request)
    return await ProxyService.forward("POST", f"{settings.auth_service_url}/auth/login", await request.json())

@router.post("/patients")
async def create_patient(request: Request):
    rate_guard(request)
    auth_guard(request, {"admin"})
    return await ProxyService.forward("POST", f"{settings.patient_service_url}/patients", await request.json())

@router.get("/patients/{patient_id}")
async def get_patient(patient_id: int, request: Request):
    rate_guard(request)
    auth_guard(request, {"admin", "doctor", "patient"})
    return await ProxyService.forward("GET", f"{settings.patient_service_url}/patients/{patient_id}")

@router.put("/patients/{patient_id}")
async def update_patient(patient_id: int, request: Request):
    rate_guard(request)
    auth_guard(request, {"admin", "patient"})
    return await ProxyService.forward("PUT", f"{settings.patient_service_url}/patients/{patient_id}", await request.json())

@router.post("/doctors")
async def create_doctor(request: Request):
    rate_guard(request)
    auth_guard(request, {"admin"})
    return await ProxyService.forward("POST", f"{settings.doctor_service_url}/doctors", await request.json())

@router.get("/doctors/{doctor_id}")
async def get_doctor(doctor_id: int, request: Request):
    rate_guard(request)
    auth_guard(request, {"admin", "doctor", "patient"})
    return await ProxyService.forward("GET", f"{settings.doctor_service_url}/doctors/{doctor_id}")

@router.put("/doctors/{doctor_id}")
async def update_doctor(doctor_id: int, request: Request):
    rate_guard(request)
    auth_guard(request, {"admin", "doctor"})
    return await ProxyService.forward("PUT", f"{settings.doctor_service_url}/doctors/{doctor_id}", await request.json())

@router.post("/appointments")
async def create_appointment(request: Request):
    rate_guard(request)
    auth_guard(request, {"admin", "patient"})
    return await ProxyService.forward("POST", f"{settings.appointment_service_url}/appointments", await request.json())

@router.delete("/appointments/{appointment_id}")
async def cancel_appointment(appointment_id: int, request: Request):
    rate_guard(request)
    auth_guard(request, {"admin", "patient"})
    return await ProxyService.forward("DELETE", f"{settings.appointment_service_url}/appointments/{appointment_id}")
""",
)
write("api-gateway/app/main_base.py", shared_base_main.format(title="API Gateway"))
write(
    "api-gateway/app/main.py",
    """
from app.main_base import app
from app.routes.gateway_routes import router
app.include_router(router)
""",
)
write(
    "api-gateway/tests/test_gateway.py",
    """
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
@patch("app.services.proxy_service.ProxyService.forward")
def test_login_route(mock_forward):
    mock_forward.return_value = {"access_token": "x", "token_type": "bearer", "role": "admin"}
    res = client.post("/auth/login", json={"username": "admin", "password": "secret"})
    assert res.status_code == 200
""",
)

write(
    ".github/workflows/ci.yml",
    """
name: CI
on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [api-gateway, auth-service, patient-service, doctor-service, appointment-service, notification-service]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: |
          python -m pip install --upgrade pip
          pip install -r ${{ matrix.service }}/requirements.txt
      - run: pytest -q ${{ matrix.service }}/tests
  docker-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker compose build
""",
)

write(
    "README.md",
    """
# Hospital Management System (Microservices)

## Services
- API Gateway (`8000`)
- Auth Service (`8001`)
- Patient Service (`8002`)
- Doctor Service (`8003`)
- Appointment Service (`8004`)
- Notification Service (`8005`)
- RabbitMQ (`5672`, UI: `15672`)
- Prometheus (`9090`)
- Grafana (`3000`)

## Architecture
All services use clean architecture style modules:
- `routes/` -> `services/` -> `models/` -> `database/`
- `schemas/` for DTO validation
- `config/` for environment and logging

## Features
- JWT auth with roles (`admin`, `doctor`, `patient`)
- API gateway routing + token guard + rate limiting
- Patient and Doctor management
- Appointment booking/canceling with cross-service validation
- RabbitMQ async events consumed by notification service
- `/health` + `/metrics` for each service
- Prometheus and Grafana included

## Run
```bash
docker compose up --build
```

## CI/CD
GitHub Actions workflow in `.github/workflows/ci.yml`:
- installs service dependencies
- runs tests for every service
- builds Docker images
""",
)

print("Generated hospital system.")
