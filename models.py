"""Weather data models."""

from typing import Optional
from pydantic import BaseModel


class Location(BaseModel):
    """Geographic location data."""

    name: str
    latitude: float
    longitude: float
    country: str
    area_1: Optional[str] = None
    area_2: Optional[str] = None


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
    area_1: Optional[str] = None
    area_2: Optional[str] = None
    temperature_fahrenheit: float
    precipitation_inch: float
