from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(
    title="Weather API", description="Simple weather API"
)


class WeatherResponse(BaseModel):
    location: str
    latitude: float
    longitude: float
    temperature_celsius: float
    precipitation_mm: float


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

    # Stub response for now
    return WeatherResponse(
        location=location,
        latitude=39.7392,
        longitude=-104.9903,
        temperature_celsius=15.2,
        precipitation_mm=0.0,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
