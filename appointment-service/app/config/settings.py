from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    service_name: str = "appointment-service"
    patient_service_url: str = "http://patient-service:8002"
    doctor_service_url: str = "http://doctor-service:8003"
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
settings = Settings()
