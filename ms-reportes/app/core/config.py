from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://reportes_user:reportes_secret@localhost:5438/reportes_db"
    service_name: str = "ms-reportes"
    ms_catalogos_url: str = "http://localhost:8001"
    ms_inventario_url: str = "http://localhost:8002"
    ms_compras_url: str = "http://localhost:8004"
    ms_ventas_url: str = "http://localhost:8005"
    ms_finanzas_url: str = "http://localhost:8006"


settings = Settings()
