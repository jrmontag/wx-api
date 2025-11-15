from typing_extensions import Annotated
import logging

from fastapi import FastAPI, HTTPException, Depends

from config import settings
from services.geocoding import GeocodingService
from services.weather import WeatherService
from models import WeatherResponse, Location
from exceptions import (
    LocationNotFoundError,
    ExternalServiceError,
    DataParseError,
)


app = FastAPI(title=settings.app_title, description=settings.app_description)

logging.basicConfig(level=logging.DEBUG)

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
        # Get location data (coordinates and country)
        location_data: Location = await geocoding_service.get_coordinates(location)

        # Get weather for those coordinates
        weather = await weather_service.get_weather(
            location_data.latitude, location_data.longitude
        )

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
