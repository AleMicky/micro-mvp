from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ms_catalogos_url: str = "http://localhost:8001"
    ms_inventario_url: str = "http://localhost:8002"
    ms_auth_url: str = "http://localhost:8003"
    ms_compras_url: str = "http://localhost:8004"
    ms_ventas_url: str = "http://localhost:8005"
    ms_finanzas_url: str = "http://localhost:8006"
    ms_reportes_url: str = "http://localhost:8007"
    ms_company_url: str = "http://localhost:8008"
    ms_clientes_url: str = "http://localhost:8009"
    ms_notificaciones_url: str = "http://localhost:8010"
    ms_chatbot_url: str = "http://localhost:8011"
    cors_origins: str = "http://localhost:3000"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"


settings = Settings()
