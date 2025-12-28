# Weather API Project Requirements

## Project Overview
A simple weather API with basic web interface for retrieving and displaying weather forecasts at user-specified locations.

## Core Features

### Phase 1 (Initial Implementation)
- Retrieve weather forecasts via third-party API integration
- Support location input (postal codes, city names)
- Return temperature and precipitation data
- Testing via OpenAPI docs or direct HTTP requests

### Future Enhancements
- Short-term caching to avoid redundant API calls
- Additional weather fields (humidity, wind speed, etc.)
- User-submitted weather reports (coexist with official data, no moderation initially)

## Technical Specifications

### Technology Stack
- **Framework**: FastAPI (async-first, auto-generated docs)
- **Package Management**: uv
- **Weather Data**: Open-Meteo API
  - Free, no API key required
  - Rate limit: ~10,000 requests/day
  - CC BY 4.0 license
- **Geocoding**: Open-Meteo Geocoding API
  - Handles flexible location formats
  - Returns lat/lon for weather queries

### Scale & Performance
- Expected traffic: ~10 requests/minute
- Low-traffic application suitable for serverless deployment

### Caching Strategy (Future Enhancement)
- Short-term only (minutes to hours)
- Purpose: Reduce API calls for repeated location queries
- Avoid hitting rate limits
- Implementation: In-memory cache (e.g., cachetools, TTLCache)
- Geocoding cache: 24 hours TTL
- Weather cache: 30-60 minutes TTL

## User Input
- Postal codes (zip codes)
- City names
- Backend handles geocoding to lat/lon for API calls

## API Specifications

### Endpoints
- `GET /weather?location={location}` - Retrieve weather for specified location

### Response Data
**Initial Implementation:**
- Temperature (current)
- Precipitation

**Future Extensions:**
- Humidity, wind speed, conditions, hourly/daily forecasts

### Location Handling
- Ambiguous locations: Always use first geocoding result
- No results found: Return error

### Error Responses
- Standard HTTP status codes
- JSON error details
- `404`: Location not found
- `503`: External API unavailable
- `429`: Rate limit exceeded
- `400`: Invalid input

## Deployment
- Target: Container-based serverless approach
- Options under consideration: Modal vs AWS Lambda
- Priority: Local development first, deployment details deferred

## Project Management
- Design should facilitate breakdown into discrete tasks
- Tasks should be suitable for LLM agent implementation