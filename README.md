# wx-api

A simple weather API built with FastAPI, easy to deploy as an AWS Lambda zip archive. Built as an exercise in collaborating with a coding agent.

## Features

- Get current temperature and precipitation for any city or postal code
- FastAPI with automatic OpenAPI documentation
- Geocoding support for flexible location input
- In-memory TTL caching (15 minutes)
- AWS Lambda deployment with cost protection

## Quick Start

### Local Development

```bash
# Install dependencies
uv sync

# Run the API
uv run fastapi dev

# Visit http://localhost:8000/docs for interactive API documentation
```

### Example Request

```bash
curl "http://localhost:8000/weather?location=Denver"
```

**Response:**
```json
{
  "location": "Denver",
  "latitude": 39.73915,
  "longitude": -104.9847,
  "country": "United States",
  "area_1": "Colorado",
  "area_2": "Denver",
  "temperature_fahrenheit": 36.2,
  "precipitation_inch": 0.0
}
```

## Testing

```bash
# Run tests
uv run pytest -v tests

# Run linter
uv run ruff check

# Format code
uv run ruff format
```

## Deployment

The API is deployed to AWS Lambda using [mangum](https://mangum.fastapiexpert.com), with DDoS protection and cost controls. See [docs/lambda-deployment.md](docs/lambda-deployment.md) for deployment notes.


## Documentation

- [Architecture](docs/architecture.md) - System design and component specifications
- [Requirements](docs/requirements.md) - Project requirements and features
- [Tasks](docs/tasks.md) - Implementation task breakdown
- [Lambda Deployment](docs/lambda-deployment.md) - AWS deployment guide with security measures
