from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://catalogos_user:catalogos_secret@localhost:5432/catalogos_db"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    run_seed: bool = False


settings = Settings()
