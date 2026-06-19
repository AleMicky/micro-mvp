from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://company_user:company_secret@localhost:5439/company_db"
    service_name: str = "ms-company"
    run_seed: bool = False


settings = Settings()
