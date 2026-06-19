from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://notif_user:notif_secret@localhost:5441/notificaciones_db"
    service_name: str = "ms-notificaciones"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"


settings = Settings()
