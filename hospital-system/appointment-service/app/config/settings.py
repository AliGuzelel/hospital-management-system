from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)

    service_name: str = "appointment-service"
    database_url: str = Field(
        default="sqlite+aiosqlite:///./appointment.db",
        alias="APPOINTMENT_DATABASE_URL",
    )
    jwt_secret: str = Field(default="dev-insecure-secret", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256")

    patient_service_url: str = Field(
        default="http://localhost:8002",
        alias="PATIENT_SERVICE_URL",
    )
    doctor_service_url: str = Field(
        default="http://localhost:8003",
        alias="DOCTOR_SERVICE_URL",
    )

    internal_service_token: str = Field(default="dev-internal", alias="INTERNAL_SERVICE_TOKEN")

    rabbitmq_url: str = Field(
        default="amqp://guest:guest@localhost:5672/",
        alias="RABBITMQ_URL",
    )
    rabbitmq_exchange: str = Field(default="hospital.events", alias="RABBITMQ_EXCHANGE")

    @field_validator("jwt_secret", "jwt_algorithm", mode="before")
    @classmethod
    def _strip_jwt_env(cls, v):  # noqa: ANN001
        if isinstance(v, str):
            return v.replace("\r", "").strip()
        return v


settings = Settings()
