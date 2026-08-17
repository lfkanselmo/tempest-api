from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    cors_origins: list[str] = ["http://localhost:4200"]
    database_url: str = "sqlite:///./data/tempest.db"
    nominatim_user_agent: str = "tempest-app (contacto no configurado)"


settings = Settings()
