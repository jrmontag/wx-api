from fastapi import FastAPI, HTTPException

from services.geocoding import GeocodingService
from services.weather import WeatherService
from models.weather import WeatherResponse
from exceptions import (
    LocationNotFoundError,
    ExternalServiceError,
    DataParseError,
)


app = FastAPI(
    title="Weather API", description="Simple weather API with Open-Meteo integration"
)


@app.get("/weather", response_model=WeatherResponse)
async def get_weather(location: str) -> WeatherResponse:
    """
    Get current weather for a specified location.

    - **location**: City name or postal code (e.g., "Denver", "80202")
    """
    if not location or location.strip() == "":
        raise HTTPException(
            status_code=400, detail="Location parameter cannot be empty"
        )

    try:
        # Get coordinates from location string
        geocoding_service = GeocodingService()
        latitude, longitude = await geocoding_service.get_coordinates(location)

        # Get weather for those coordinates
        weather_service = WeatherService()
        weather = await weather_service.get_weather(latitude, longitude)

        return WeatherResponse(
            location=location,
            latitude=latitude,
            longitude=longitude,
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
