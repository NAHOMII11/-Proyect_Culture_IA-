from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = (
        "postgresql+psycopg://config_user:config_password@localhost:5435/config_db"
    )
    app_title: str = "Config Service"


settings = Settings()
