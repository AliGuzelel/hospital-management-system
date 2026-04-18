from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    service_name: str = "notification-service"
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
settings = Settings()
