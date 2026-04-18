from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)

    service_name: str = "auth-service"
    database_url: str = Field(
        default="sqlite+aiosqlite:///./auth.db",
        alias="AUTH_DATABASE_URL",
    )
    jwt_secret: str = Field(default="dev-insecure-secret", alias="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    @field_validator("jwt_secret", "jwt_algorithm", mode="before")
    @classmethod
    def _strip_jwt_env(cls, v):  # noqa: ANN001
        if isinstance(v, str):
            return v.replace("\r", "").strip()
        return v


settings = Settings()
