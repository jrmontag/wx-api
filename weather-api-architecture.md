# Weather API Architecture & Implementation Plan

## Architecture Overview

### Request Flow
1. Client → `GET /weather?location={location}`
2. FastAPI validates input (non-empty string)
3. GeocodingService: location string → lat/lon
4. WeatherService: lat/lon → weather data
5. Response: JSON with temperature and precipitation
6. Error handling at each step

### Component Structure

```
weather-api/
├── main.py                 # FastAPI app, endpoint definitions
├── services/
│   ├── __init__.py
│   ├── geocoding.py        # GeocodingService
│   └── weather.py          # WeatherService
├── models/
│   ├── __init__.py
│   ├── requests.py         # Request models (if needed)
│   └── responses.py        # Response models
├── config.py               # Configuration (API URLs, constants)
├── exceptions.py           # Custom exceptions
├── pyproject.toml          # uv project configuration
└── tests/                  # Future: unit and integration tests
```

## Component Specifications

### 1. API Layer (`main.py`)

**Endpoint:**
```python
@app.get("/weather")
async def get_weather(location: str) -> WeatherResponse
```

**Responsibilities:**
- Input validation (location is non-empty string)
- Orchestrate service calls
- Error handling and HTTP status code mapping
- Return structured JSON response

**Error Handling:**
- `400 Bad Request`: Empty/invalid location parameter
- `404 Not Found`: No geocoding results for location
- `503 Service Unavailable`: External API failure
- `500 Internal Server Error`: Unexpected errors

### 2. GeocodingService (`services/geocoding.py`)

**Responsibilities:**
- Call Open-Meteo Geocoding API
- Parse response, extract first result
- Return lat/lon coordinates
- Raise exception if no results found

**API Details:**
- Endpoint: `https://geocoding-api.open-meteo.com/v1/search`
- Parameters: `name={location}`
- Returns: Array of results with `latitude`, `longitude`, `name`, etc.

**Error Scenarios:**
- Empty results array → LocationNotFoundError
- Network/API error → ExternalServiceError

### 3. WeatherService (`services/weather.py`)

**Responsibilities:**
- Call Open-Meteo Weather API with lat/lon
- Extract temperature and precipitation from response
- Return structured data
- Handle API errors

**API Details:**
- Endpoint: `https://api.open-meteo.com/v1/forecast`
- Parameters: 
  - `latitude={lat}`
  - `longitude={lon}`
  - `current=temperature_2m,precipitation`
- Returns: Current weather data

**Error Scenarios:**
- Network/API error → ExternalServiceError
- Invalid response format → DataParseError

### 4. Models (`models/responses.py`)

**WeatherResponse:**
```python
class WeatherResponse(BaseModel):
    location: str              # Original input
    latitude: float
    longitude: float
    temperature_celsius: float
    precipitation_mm: float
```

**ErrorResponse:**
```python
class ErrorResponse(BaseModel):
    error: str                 # Error type
    message: str               # Human-readable message
    detail: Optional[str]      # Additional context
```

### 5. Configuration (`config.py`)

- API base URLs
- Timeout values
- Default parameters
- Constants

### 6. Exceptions (`exceptions.py`)

Custom exceptions:
- `LocationNotFoundError`: No geocoding results
- `ExternalServiceError`: API unavailable/timeout
- `DataParseError`: Unexpected response format

## Implementation

See [weather-api-tasks.md](weather-api-tasks.md) for the detailed task breakdown and implementation sequence.

## Testing Strategy

**Manual Testing (Initial):**
- Use FastAPI's auto-generated OpenAPI docs at `/docs`
- Test cases:
  - Valid city: "Denver"
  - Valid postal code: "80202"
  - Ambiguous city: "Springfield"
  - Invalid location: "asdfghjkl"
  - Empty string
  - Special characters

**Future Automated Testing:**
- Unit tests for each service
- Integration tests for full endpoint
- Mock external API calls
- Test error scenarios

## Running the Application

```bash
# Development
uvicorn main:app --reload

# Access docs
http://localhost:8000/docs

# Test endpoint
curl "http://localhost:8000/weather?location=Denver"
```

## Notes

- All HTTP calls should be async (use httpx.AsyncClient)
- Set reasonable timeouts (5-10 seconds)
- Log all external API calls for debugging
- Open-Meteo doesn't require API keys (simpler for now)
- Consider rate limiting in future if needed
