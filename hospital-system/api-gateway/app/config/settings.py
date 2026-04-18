from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)

    service_name: str = "api-gateway"

    jwt_secret: str = Field(default="dev-insecure-secret", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")

    auth_service_url: str = Field(default="http://localhost:8001", alias="AUTH_SERVICE_URL")
    patient_service_url: str = Field(default="http://localhost:8002", alias="PATIENT_SERVICE_URL")
    doctor_service_url: str = Field(default="http://localhost:8003", alias="DOCTOR_SERVICE_URL")
    appointment_service_url: str = Field(
        default="http://localhost:8004",
        alias="APPOINTMENT_SERVICE_URL",
    )

    rate_limit_requests: int = Field(default=120, alias="RATE_LIMIT_REQUESTS")
    rate_limit_window_seconds: int = Field(default=60, alias="RATE_LIMIT_WINDOW_SECONDS")

    downstream_timeout_seconds: float = Field(default=10.0, alias="GATEWAY_DOWNSTREAM_TIMEOUT_SECONDS")

    @field_validator("jwt_secret", "jwt_algorithm", mode="before")
    @classmethod
    def _strip_jwt_env(cls, v):  # noqa: ANN001
        if isinstance(v, str):
            return v.replace("\r", "").strip()
        return v


settings = Settings()
