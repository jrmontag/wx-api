import logging

import httpx

from config import settings
from models import Location

logger = logging.getLogger(__name__)


class GeocodingService:
    """Service for converting location names to coordinates using Open-Meteo Geocoding API."""

    async def get_coordinates(self, location: str) -> Location:
        """
        Convert a location string to geographic coordinates.

        Args:
            location: City name or postal code (e.g., "Denver", "80202")

        Returns:
            Location object with name, latitude, longitude, and country

        Raises:
            LocationNotFoundError: If no results found for the location
            ExternalServiceError: If API call fails
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    settings.geocoding_base_url,
                    params={"name": location, "count": settings.geocoding_result_count},
                    timeout=settings.geocoding_timeout,
                )
                response.raise_for_status()
                data = response.json()

                # Check if we got any results
                results = data.get("results", [])
                if not results:
                    from exceptions import LocationNotFoundError

                    raise LocationNotFoundError(f"No location found for: {location}")

                # Return first result as Location object
                first_result = results[0]
                latitude = first_result["latitude"]
                longitude = first_result["longitude"]
                name = first_result["name"]
                country = first_result["country"]
                area_1 = first_result.get("admin1")
                area_2 = first_result.get("admin2")

                logger.debug(
                    f"Geocoded location: {name}, {country} → ({latitude}, {longitude})"
                )

                return Location(
                    name=name,
                    latitude=latitude,
                    longitude=longitude,
                    country=country,
                    area_1=area_1,
                    area_2=area_2,
                )

        except httpx.HTTPStatusError as e:
            from exceptions import ExternalServiceError

            raise ExternalServiceError(
                f"Geocoding API returned status {e.response.status_code}"
            ) from e
        except (httpx.RequestError, TimeoutError) as e:
            from exceptions import ExternalServiceError

            raise ExternalServiceError(
                f"Failed to connect to Geocoding API: {e}"
            ) from e
        except KeyError as e:
            from exceptions import DataParseError

            raise DataParseError(
                f"Unexpected response format from Geocoding API: {e}"
            ) from e
