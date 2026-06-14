from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = (
        "postgresql+asyncpg://inventario_user:inventario_secret@localhost:5433/inventario_db"
    )
    service_name: str = "ms-inventario"
    run_seed: bool = False
    ms_catalogos_url: str = "http://localhost:8001"


settings = Settings()
