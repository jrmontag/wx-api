import logging

import httpx

from models.weather import WeatherStatus

logger = logging.getLogger(__name__)


class WeatherService:
    """Service for fetching weather data using Open-Meteo Weather API."""

    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    TIMEOUT = 10.0

    async def get_weather(self, latitude: float, longitude: float) -> WeatherStatus:
        """
        Fetch current weather data for given coordinates.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            WeatherStatus object with temperature_fahrenheit and precipitation_inch

        Raises:
            ExternalServiceError: If API call fails
            DataParseError: If response format is unexpected
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.BASE_URL,
                    params={
                        "latitude": latitude,
                        "longitude": longitude,
                        "current": "temperature_2m,precipitation",
                        "forecast_days": 1,
                        "temperature_unit": "fahrenheit",
                        "wind_speed_unit": "mph",
                        "precipitation_unit": "inch",
                    },
                    timeout=self.TIMEOUT,
                )
                response.raise_for_status()
                data = response.json()

                # Extract current weather data
                current = data["current"]
                temperature_fahrenheit = current["temperature_2m"]
                precipitation_inch = current["precipitation"]

                logger.debug(
                    f"Weather at ({latitude}, {longitude}): "
                    f"Temp={temperature_fahrenheit}°F, Precip={precipitation_inch}in"
                )

                return WeatherStatus(
                    temperature_fahrenheit=temperature_fahrenheit,
                    precipitation_inch=precipitation_inch,
                )

        except httpx.HTTPStatusError as e:
            from exceptions import ExternalServiceError

            raise ExternalServiceError(
                f"Weather API returned status {e.response.status_code}"
            ) from e
        except (httpx.RequestError, TimeoutError) as e:
            from exceptions import ExternalServiceError

            raise ExternalServiceError(f"Failed to connect to Weather API: {e}") from e
        except KeyError as e:
            from exceptions import DataParseError

            raise DataParseError(
                f"Unexpected response format from Weather API: {e}"
            ) from e
