from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "postgresql+asyncpg://ventas_user:ventas_secret@localhost:5436/ventas_db"
    service_name: str = "ms-ventas"
    run_seed: bool = False
    ms_inventario_url: str = "http://localhost:8002"
    ms_finanzas_url: str = "http://localhost:8006"

settings = Settings()
