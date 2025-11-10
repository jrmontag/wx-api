"""Integration tests for Weather API endpoints."""

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


def test_weather_endpoint_valid_city(client):
    """Test /weather endpoint with a valid city name."""
    response = client.get("/weather?location=Denver")

    assert response.status_code == 200
    data = response.json()
    assert data["location"] == "Denver"
    assert isinstance(data["latitude"], float)
    assert isinstance(data["longitude"], float)
    assert isinstance(data["temperature_fahrenheit"], float)
    assert isinstance(data["precipitation_inch"], float)


def test_weather_endpoint_valid_postal_code(client):
    """Test /weather endpoint with a valid postal code."""
    response = client.get("/weather?location=80202")

    assert response.status_code == 200
    data = response.json()
    assert data["location"] == "80202"
    assert isinstance(data["latitude"], float)
    assert isinstance(data["longitude"], float)
    assert isinstance(data["temperature_fahrenheit"], float)
    assert isinstance(data["precipitation_inch"], float)


def test_weather_endpoint_ambiguous_location(client):
    """Test /weather endpoint with ambiguous location (uses first result)."""
    response = client.get("/weather?location=Springfield")

    assert response.status_code == 200
    data = response.json()
    assert data["location"] == "Springfield"
    assert isinstance(data["latitude"], float)
    assert isinstance(data["longitude"], float)


def test_weather_endpoint_invalid_location(client):
    """Test /weather endpoint with invalid location returns 404."""
    response = client.get("/weather?location=asdfghjkl")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data or "error" in data


def test_weather_endpoint_empty_location(client):
    """Test /weather endpoint with empty location returns 400."""
    response = client.get("/weather?location=")

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_weather_endpoint_missing_location(client):
    """Test /weather endpoint without location parameter returns 422."""
    response = client.get("/weather")

    assert response.status_code == 422
