"""
Weather Service - Handles weather-related operations
"""

import logging
import requests
from typing import Dict, Optional, List

from app.models.weather_codes import WEATHER_CODES

logger = logging.getLogger(__name__)

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODE_API_URL = "https://geocoding-api.open-meteo.com/v1/reverse"


def fetch_location_name(lat: float, lon: float) -> Dict[str, str]:
    """Fetch location name from coordinates using geocoding API"""
    try:
        resp = requests.get(
            GEOCODE_API_URL,
            params={"latitude": lat, "longitude": lon, "language": "en"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if not data.get("results"):
            return {}
        top = data["results"][0]
        return {
            "name": top.get("name"),
            "region": top.get("admin1") or top.get("admin2"),
            "country": top.get("country"),
        }
    except requests.RequestException:
        return {}


def advise_for_weather(temp_c: float, condition_code: int) -> str:
    """Generate weather advice based on temperature and condition"""
    condition = WEATHER_CODES.get(condition_code, "").lower()
    advice_parts: List[str] = []

    if temp_c <= 5:
        advice_parts.append("Bundle up — it's quite chilly.")
    elif temp_c >= 28:
        advice_parts.append("Stay hydrated, it's pretty warm.")
    elif 5 < temp_c < 28:
        advice_parts.append("Looks like comfortable weather outside.")

    if "rain" in condition or "drizzle" in condition or condition_code in {80, 81, 82}:
        advice_parts.append("Keep an umbrella nearby.")
    if "snow" in condition or condition_code in {85, 86}:
        advice_parts.append("Watch your step — snow is expected.")
    if condition_code in {45, 48}:
        advice_parts.append("Visibility is low, drive carefully.")
    if condition_code in {95, 96, 99}:
        advice_parts.append("There's a storm brewing, best to stay indoors if possible.")

    if not advice_parts:
        advice_parts.append("A great moment to get some fresh air.")

    return " ".join(advice_parts)


def get_weather_data(lat: float, lon: float) -> Dict:
    """Fetch weather data for given coordinates"""
    response = requests.get(
        WEATHER_API_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code",
            "timezone": "auto",
        },
        timeout=10,
    )
    response.raise_for_status()
    payload = response.json()
    current = payload.get("current")
    if not current:
        raise ValueError("No current weather data")

    code = int(current.get("weather_code", 0))
    condition = WEATHER_CODES.get(code, "Unknown conditions")
    advice = advise_for_weather(current.get("temperature_2m", 0.0), code)
    location = fetch_location_name(lat, lon)

    return {
        "location": {
            "name": location.get("name"),
            "region": location.get("region"),
            "country": location.get("country"),
            "latitude": lat,
            "longitude": lon,
        },
        "current": {
            "temperature": current.get("temperature_2m"),
            "apparent_temperature": current.get("apparent_temperature"),
            "humidity": current.get("relative_humidity_2m"),
            "wind_speed": current.get("wind_speed_10m"),
            "condition_code": code,
            "condition": condition,
            "time": current.get("time"),
        },
        "advice": advice,
    }
