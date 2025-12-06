from http.server import BaseHTTPRequestHandler
import json
import sys
from urllib.parse import parse_qs, urlparse

import requests

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODE_API_URL = "https://geocoding-api.open-meteo.com/v1/reverse"

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
    55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow", 77: "Snow grains",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    85: "Slight snow showers", 86: "Heavy snow showers", 95: "Thunderstorm",
    96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
}

def fetch_location_name(lat: float, lon: float) -> str:
    """Fetch location name from coordinates."""
    try:
        response = requests.get(
            GEOCODE_API_URL,
            params={"latitude": lat, "longitude": lon, "count": 1},
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("results"):
            location = data["results"][0]
            name = location.get("name", "Unknown")
            admin1 = location.get("admin1", "")
            country = location.get("country", "")
            return f"{name}, {admin1}, {country}" if admin1 else f"{name}, {country}"
        
        return f"{lat:.2f}°, {lon:.2f}°"
    except Exception:
        return f"{lat:.2f}°, {lon:.2f}°"

def advise_for_weather(weather_code: int, temp: float) -> str:
    """Generate weather advice."""
    condition = WEATHER_CODES.get(weather_code, "Unknown conditions")
    advice = []
    
    if weather_code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
        advice.append("Don't forget your umbrella!")
    if weather_code in [71, 73, 75, 77, 85, 86]:
        advice.append("Dress warmly and watch for icy conditions.")
    if weather_code in [95, 96, 99]:
        advice.append("Stay indoors if possible. Thunderstorm in the area!")
    
    if temp < 0:
        advice.append("It's freezing out there! Bundle up.")
    elif temp < 10:
        advice.append("It's quite cold. Wear a jacket.")
    elif temp > 30:
        advice.append("It's hot! Stay hydrated.")
    
    return " ".join(advice) if advice else "Have a great day!"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            parsed_path = urlparse(self.path)
            params = parse_qs(parsed_path.query)
            
            lat = params.get('lat', [None])[0]
            lon = params.get('lon', [None])[0]
            
            if not lat or not lon:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Missing lat/lon parameters"}).encode())
                return
            
            try:
                lat, lon = float(lat), float(lon)
            except ValueError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid lat/lon values"}).encode())
                return
            
            response = requests.get(
                WEATHER_API_URL,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code",
                    "timezone": "auto"
                },
                timeout=10
            )
            response.raise_for_status()
            payload = response.json()
            current = payload.get("current")
            if not current:
                raise ValueError("No current weather data")
            
            code = int(current.get("weather_code", 0))
            condition = WEATHER_CODES.get(code, "Unknown conditions")
            location_name = fetch_location_name(lat, lon)
            temp = current.get("temperature_2m", 0.0)
            
            # Parse location name
            location_parts = location_name.split(", ")
            location_obj = {
                "name": location_parts[0] if len(location_parts) > 0 else "Unknown",
                "region": location_parts[1] if len(location_parts) > 1 else "",
                "country": location_parts[2] if len(location_parts) > 2 else location_parts[-1] if location_parts else "",
                "latitude": lat,
                "longitude": lon
            }
            
            result = {
                "location": location_obj,
                "current": {
                    "temperature": current.get("temperature_2m"),
                    "apparent_temperature": current.get("apparent_temperature"),
                    "humidity": current.get("relative_humidity_2m"),
                    "wind_speed": current.get("wind_speed_10m"),
                    "condition_code": code,
                    "condition": condition,
                    "time": current.get("time")
                },
                "advice": advise_for_weather(code, temp)
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            print(f"Weather error: {e}", file=sys.stderr)
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
