from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "auth-service"
    jwt_secret: str = "super-secret-change-me"
    jwt_algorithm: str = "HS256"

    @field_validator("jwt_secret", "jwt_algorithm", mode="before")
    @classmethod
    def _strip_jwt_env(cls, v):
        if isinstance(v, str):
            return v.replace("\r", "").replace("\ufeff", "").strip()
        return v
    access_token_expire_minutes: int = 60
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
