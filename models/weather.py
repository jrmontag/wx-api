"""Weather data models."""

from pydantic import BaseModel


class WeatherStatus(BaseModel):
    """Current weather status data."""

    temperature_fahrenheit: float
    precipitation_inch: float


class WeatherResponse(BaseModel):
    """Weather API response model."""

    location: str
    latitude: float
    longitude: float
    temperature_fahrenheit: float
    precipitation_inch: float
