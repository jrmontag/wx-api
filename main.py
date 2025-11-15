from typing import Optional
from typing_extensions import Annotated
import logging

from fastapi import FastAPI, HTTPException, Depends

from cache import SimpleTTLCache
from config import settings
from services.geocoding import GeocodingService
from services.weather import WeatherService
from models import WeatherResponse, Location, WeatherStatus
from exceptions import (
    LocationNotFoundError,
    ExternalServiceError,
    DataParseError,
)


app = FastAPI(title=settings.app_title, description=settings.app_description)
shared_cache = SimpleTTLCache(ttl_seconds=900)


logging.basicConfig(level=logging.INFO)


def get_geocoding_service() -> GeocodingService:
    """Dependency for GeocodingService."""
    return GeocodingService()


def get_weather_service() -> WeatherService:
    """Dependency for WeatherService."""
    return WeatherService()


@app.get("/weather", response_model=WeatherResponse)
async def get_weather(
    location: str,
    geocoding_service: Annotated[GeocodingService, Depends(get_geocoding_service)],
    weather_service: Annotated[WeatherService, Depends(get_weather_service)],
) -> WeatherResponse:
    """
    Get current weather for a specified location.

    - **location**: City name or postal code (e.g., "Denver", "80202")
    """
    if not location or location.strip() == "":
        raise HTTPException(
            status_code=400, detail="Location parameter cannot be empty"
        )

    try:
        geo_cache_key = f"geo:{location}"
        location_data: Optional[Location] = shared_cache.get(geo_cache_key)
        if location_data is None:
            location_data = await geocoding_service.get_coordinates(location)
            shared_cache.set(geo_cache_key, location_data)

        wx_cache_key = f"wx:{location_data.latitude},{location_data.longitude}"
        weather: Optional[WeatherStatus] = shared_cache.get(wx_cache_key)
        if weather is None:
            weather = await weather_service.get_weather(
                location_data.latitude, location_data.longitude
            )
            shared_cache.set(wx_cache_key, weather)

        return WeatherResponse(
            location=location,
            latitude=location_data.latitude,
            longitude=location_data.longitude,
            country=location_data.country,
            area_1=location_data.area_1,
            area_2=location_data.area_2,
            temperature_fahrenheit=weather.temperature_fahrenheit,
            precipitation_inch=weather.precipitation_inch,
        )

    except LocationNotFoundError:
        raise HTTPException(status_code=404, detail=f"Location not found: {location}")
    except ExternalServiceError as e:
        raise HTTPException(status_code=503, detail=f"External service error: {str(e)}")
    except DataParseError as e:
        raise HTTPException(status_code=500, detail=f"Data parsing error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
