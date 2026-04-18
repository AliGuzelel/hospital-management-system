from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    service_name: str = "patient-service"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
settings = Settings()
