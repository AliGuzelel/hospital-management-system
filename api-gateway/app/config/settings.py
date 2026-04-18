from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "api-gateway"
    auth_service_url: str = "http://auth-service:8001"
    patient_service_url: str = "http://patient-service:8002"
    doctor_service_url: str = "http://doctor-service:8003"
    appointment_service_url: str = "http://appointment-service:8004"
    jwt_secret: str = "super-secret-change-me"
    jwt_algorithm: str = "HS256"

    @field_validator("jwt_secret", "jwt_algorithm", mode="before")
    @classmethod
    def _strip_jwt_env(cls, v):
        if isinstance(v, str):
            return v.replace("\r", "").replace("\ufeff", "").strip()
        return v
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
settings = Settings()
