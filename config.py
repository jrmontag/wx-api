"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with support for environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Geocoding API Configuration
    geocoding_base_url: str = "https://geocoding-api.open-meteo.com/v1/search"
    geocoding_timeout: float = 10.0
    geocoding_result_count: int = 3

    # Weather API Configuration
    weather_base_url: str = "https://api.open-meteo.com/v1/forecast"
    weather_timeout: float = 10.0

    # Application Settings
    app_title: str = "Weather API"
    app_description: str = "Simple weather API"


# Global settings instance
settings = Settings()
