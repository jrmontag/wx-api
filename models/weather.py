"""Weather data models."""

from pydantic import BaseModel


class WeatherStatus(BaseModel):
    """Current weather status data."""

    temperature_fahrenheit: float
    precipitation_inch: float
