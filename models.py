"""Weather data models."""

from pydantic import BaseModel


class Location(BaseModel):
    """Geographic location data."""

    name: str
    latitude: float
    longitude: float
    country: str


class WeatherStatus(BaseModel):
    """Current weather status data."""

    temperature_fahrenheit: float
    precipitation_inch: float


class WeatherResponse(BaseModel):
    """Weather API response model."""

    location: str
    latitude: float
    longitude: float
    country: str
    temperature_fahrenheit: float
    precipitation_inch: float
