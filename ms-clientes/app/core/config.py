from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://clientes_user:clientes_secret@localhost:5440/clientes_db"
    service_name: str = "ms-clientes"
    run_seed: bool = False
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"


settings = Settings()
