from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FastAPI Gateway + BFF"
    app_version: str = "1.0.0"
    environment: str = "dev"

    # AQUÍ ESTAN LAS APIS QUE LLAMA DE LOS DEMAS CONTENEDORES
    
    auth_api_url: str = "http://cultureia-auth-api:8001"
    geo_api_url: str = "http://cultureia-geo-api:8002"
    places_api_url: str = "http://api_place_container:8003"
    config_api_url: str = "http://config_api:8004"
    quality_api_url: str = "http://api-quality:8005"
    iaenri_api_url: str = "http://api-iaenri:8006"

    request_timeout_seconds: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()