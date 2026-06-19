from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://ventas_user:ventas_secret@localhost:5436/ventas_db"
    service_name: str = "ms-ventas"
    run_seed: bool = False
    ms_catalogos_url: str = "http://localhost:8001"
    ms_inventario_url: str = "http://localhost:8002"
    ms_finanzas_url: str = "http://localhost:8006"
    ms_clientes_url: str = "http://localhost:8009"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"


settings = Settings()
