from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = (
        "postgresql+asyncpg://chatbot_user:chatbot_secret@localhost:5442/chatbot_db"
    )
    service_name: str = "ms-chatbot"
    ms_catalogos_url: str = "http://localhost:8001"
    ms_inventario_url: str = "http://localhost:8002"
    ms_company_url: str = "http://localhost:8008"
    ms_ventas_url: str = "http://localhost:8005"
    whatsapp_cliente_id: int = 1

    whatsapp_phone_number_id: str = ""
    whatsapp_access_token: str = ""
    whatsapp_verify_token: str = ""
    whatsapp_app_secret: str = ""
    whatsapp_api_version: str = "v20.0"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    tunnel_log_path: str = ""


settings = Settings()
