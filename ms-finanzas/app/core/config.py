from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://finanzas_user:finanzas_secret@localhost:5437/finanzas_db"
    service_name: str = "ms-finanzas"
    run_seed: bool = False


settings = Settings()
