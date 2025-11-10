# Weather API Implementation Tasks

## Task Checklist

- [x] Task 1: Project Setup
- [x] Task 2: FastAPI Endpoint Skeleton
- [x] Task 3: GeocodingService
- [ ] Task 4: WeatherService
- [ ] Task 5: Integration
- [ ] Task 6: Configuration & Models
- [ ] Task 7: Testing & Refinement
- [ ] Task 8: Caching (Future)

## Task Overview

This document outlines the sequential tasks for implementing the weather API. Each task is designed to be discrete and can be executed independently by an LLM agent or developer.

## Implementation Sequence

### Task 1: Project Setup
- Initialize uv project
- Configure pyproject.toml with dependencies:
  - fastapi
  - uvicorn
  - httpx (for async HTTP calls)
  - pydantic
- Create directory structure

**Directory Structure:**
```
weather-api/
├── main.py
├── services/
│   └── __init__.py
├── models/
│   └── __init__.py
├── config.py
├── exceptions.py
├── pyproject.toml
└── tests/
```

### Task 2: FastAPI Endpoint Skeleton
- Create FastAPI app in `main.py`
- Implement `/weather` endpoint with basic structure
- Add request validation (location parameter)
- Return placeholder/stub response
- Verify endpoint accessible via `/docs`
- Test basic request/response flow

**Deliverables:**
- Working FastAPI application
- `/weather` endpoint returning stub data
- OpenAPI docs available at `/docs`

### Task 3: GeocodingService
- Implement `GeocodingService` in `services/geocoding.py`
- Handle API calls with httpx
- Parse response, return first result
- Error handling for no results and API failures
- Manual testing with known locations

**API Details:**
- Endpoint: `https://geocoding-api.open-meteo.com/v1/search`
- Parameters: `name={location}`
- Returns: Array of results with `latitude`, `longitude`, `name`, etc.

**Deliverables:**
- `services/geocoding.py` with GeocodingService class
- Method to convert location string → lat/lon
- Proper error handling and exceptions

### Task 4: WeatherService
- Implement `WeatherService` in `services/weather.py`
- Handle API calls with httpx
- Extract temperature and precipitation
- Error handling for API failures
- Manual testing with known coordinates

**API Details:**
- Endpoint: `https://api.open-meteo.com/v1/forecast`
- Parameters: 
  - `latitude={lat}`
  - `longitude={lon}`
  - `current=temperature_2m,precipitation`
- Returns: Current weather data

**Deliverables:**
- `services/weather.py` with WeatherService class
- Method to fetch weather data from lat/lon
- Proper error handling and exceptions

### Task 5: Integration
- Integrate GeocodingService into `/weather` endpoint
- Integrate WeatherService into `/weather` endpoint
- Map exceptions to HTTP status codes
- Replace stub response with actual data
- End-to-end testing

**Error Mapping:**
- `LocationNotFoundError` → 404 Not Found
- `ExternalServiceError` → 503 Service Unavailable
- `DataParseError` → 500 Internal Server Error
- Invalid input → 400 Bad Request

**Deliverables:**
- Fully functional `/weather` endpoint
- Proper error responses with JSON details
- Complete request flow: location → geocoding → weather → response

### Task 6: Configuration & Models
- Create `config.py` with API URLs
- Define response models in `models/responses.py`
- Define custom exceptions in `exceptions.py`

**Deliverables:**
- `config.py`: API base URLs, timeout values, constants
- `models/responses.py`: WeatherResponse and ErrorResponse models
- `exceptions.py`: LocationNotFoundError, ExternalServiceError, DataParseError

### Task 7: Testing & Refinement
- Test via OpenAPI docs at `/docs`
- Test various input types: cities, postal codes
- Test error scenarios: invalid locations, etc.
- Verify response format
- Document any issues or improvements

**Test Cases:**
- Valid city: "Denver"
- Valid postal code: "80202"
- Ambiguous city: "Springfield"
- Invalid location: "asdfghjkl"
- Empty string
- Special characters

**Deliverables:**
- Documented test results
- Any bug fixes or refinements
- Verification of all error scenarios

### Task 8: Caching (Future)
- Add cachetools dependency
- Implement TTL cache for geocoding (24h)
- Implement TTL cache for weather (30-60min)
- Test cache hit/miss behavior

**Deliverables:**
- In-memory caching implementation
- Cache configuration in `config.py`
- Performance improvement documentation

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
- Open-Meteo doesn't require API keys
- Each task should be completed and tested before moving to the next
