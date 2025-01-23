"""Unit tests for the HiveBox API endpoints."""

import pytest
from fastapi.testclient import TestClient

from .app import app, VERSION

client = TestClient(app)


def test_version_endpoint():
    """Test version endpoint returns correct version information."""
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": VERSION}


@pytest.mark.asyncio
async def test_temperature_endpoint():
    """Test temperature endpoint returns valid data from real sensors."""
    response = client.get("/temperature")

    assert response.status_code == 200
    assert "temperature" in response.json()

    temp = response.json()["temperature"]
    assert isinstance(temp, float)
