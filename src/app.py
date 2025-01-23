import sys
from datetime import datetime, timedelta, timezone
from typing import Dict, List

import httpx
from fastapi import FastAPI, HTTPException

VERSION = "v0.0.1"
OPENSENSEMAP_BASE_URL = "https://api.opensensemap.org/boxes"

app = FastAPI(title="HiveBox API")


@app.get("/version")
async def get_version() -> Dict[str, str]:
    """Return the current version of the application"""
    return {"version": VERSION}


async def get_sensor_temperature(sensor_id: str) -> float:
    """Fetch temperature for a specific senseBox within the last hour.

    Args:
        sensor_id: The ID of the senseBox to query

    Returns:
        float: Temperature reading from the sensor
    """
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    from_date = one_hour_ago.strftime("%Y-%m-%dT%H:%M:%SZ")
    url = f"{OPENSENSEMAP_BASE_URL}/{sensor_id}?from-date={from_date}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch data for sensor {sensor_id}"
            )

        data = response.json()
        for sensor in data.get("sensors", []):
            if "temperatur" in sensor.get("title", "").lower():
                try:
                    measurement = sensor.get("lastMeasurement", {})
                    if not measurement:
                        raise HTTPException(
                            status_code=404,
                            detail=f"No recent temperature reading for sensor {sensor_id}"
                        )
                    return float(measurement["value"])
                except (KeyError, ValueError, TypeError) as exc:
                    raise HTTPException(
                        status_code=404,
                        detail=f"No valid temperature reading for sensor {sensor_id}"
                    ) from exc

        raise HTTPException(
            status_code=404,
            detail=f"No temperature sensor found for box {sensor_id}"
        )


@app.get("/temperature")
async def get_temperature() -> Dict[str, float]:
    """Return the average temperature from specific senseBox sensors."""
    sensor_ids: List[str] = [
        "5eba5fbad46fb8001b799786",
        "5eb99cacd46fb8001b2ce04c",
        "5e60cf5557703e001bdae7f8",
    ]

    temperatures = []
    for sensor_id in sensor_ids:
        temp = await get_sensor_temperature(sensor_id)
        temperatures.append(temp)

    if not temperatures:
        raise HTTPException(status_code=404, detail="No temperature readings available")

    return {"temperature": round(sum(temperatures) / len(temperatures), 2)}


def print_version():
    """Print the current version of the application and exit."""
    sys.exit(0)


if __name__ == "__main__":
    print_version()
