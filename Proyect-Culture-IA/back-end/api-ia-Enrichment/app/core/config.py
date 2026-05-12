from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Enrichment Service"
    app_env: str = "dev"

    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "places"
    postgres_host: str = "db"
    postgres_port: int = 5432
    audit_service_url: str = "http://host.docker.internal:8007"
    audit_timeout_seconds: int = 5

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()