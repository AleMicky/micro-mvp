from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://compras_user:compras_secret@localhost:5435/compras_db"
    service_name: str = "ms-compras"
    run_seed: bool = False
    ms_inventario_url: str = "http://ms-inventario:8002"
    ms_finanzas_url: str = "http://localhost:8006"


settings = Settings()
