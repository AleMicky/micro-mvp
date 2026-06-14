from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ms_catalogos_url: str = "http://localhost:8001"
    ms_inventario_url: str = "http://localhost:8002"
    cors_origins: str = "http://localhost:3000"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"


settings = Settings()
