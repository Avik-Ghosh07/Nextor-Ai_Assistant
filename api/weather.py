from http.server import BaseHTTPRequestHandler
import json
import requests
import sys
from urllib.parse import parse_qs, urlparse

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODE_API_URL = "https://geocoding-api.open-meteo.com/v1/reverse"

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Depositing rime fog", 51: "Light drizzle",
    53: "Moderate drizzle", 55: "Dense drizzle", 56: "Light freezing drizzle",
    57: "Dense freezing drizzle", 61: "Slight rain", 63: "Moderate rain",
    65: "Heavy rain", 66: "Light freezing rain", 67: "Heavy freezing rain",
    71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
    77: "Snow grains", 80: "Rain showers", 81: "Heavy rain showers",
    82: "Violent rain showers", 85: "Snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

def fetch_location_name(lat, lon):
    try:
        resp = requests.get(GEOCODE_API_URL, params={
            "latitude": lat, "longitude": lon, "language": "en"
        }, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("results"):
            top = data["results"][0]
            return {
                "name": top.get("name"),
                "region": top.get("admin1") or top.get("admin2"),
                "country": top.get("country")
            }
    except:
        pass
    return {}

def advise_for_weather(temp_c, condition_code):
    condition = WEATHER_CODES.get(condition_code, "").lower()
    advice_parts = []

    if temp_c <= 5:
        advice_parts.append("Bundle up — it's quite chilly.")
    elif temp_c >= 28:
        advice_parts.append("Stay hydrated, it's pretty warm.")
    else:
        advice_parts.append("Looks like comfortable weather outside.")

    if "rain" in condition or "drizzle" in condition or condition_code in {80, 81, 82}:
        advice_parts.append("Keep an umbrella nearby.")
    if "snow" in condition or condition_code in {85, 86}:
        advice_parts.append("Watch your step — snow is expected.")
    if condition_code in {45, 48}:
        advice_parts.append("Visibility is low, drive carefully.")
    if condition_code in {95, 96, 99}:
        advice_parts.append("There's a storm brewing, best to stay indoors if possible.")

    return " ".join(advice_parts) if advice_parts else "A great moment to get some fresh air."

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        lat = params.get('lat', [None])[0]
        lon = params.get('lon', [None])[0]
        
        if not lat or not lon:
            print(f"Weather error: Missing lat/lon parameters", file=sys.stderr)
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "lat and lon parameters are required"}).encode())
            return
        
        try:
            lat_f, lon_f = float(lat), float(lon)
            print(f"Fetching weather for lat={lat_f}, lon={lon_f}", file=sys.stderr)
            
            # Fetch weather data
            resp = requests.get(WEATHER_API_URL, params={
                "latitude": lat_f,
                "longitude": lon_f,
                "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code",
                "timezone": "auto"
            }, timeout=15)
            resp.raise_for_status()
            weather_data = resp.json()
            print(f"Weather API response received", file=sys.stderr)
            
            current = weather_data.get("current", {})
            if not current:
                raise ValueError("No current weather data")
            
            code = int(current.get("weather_code", 0))
            temp = current.get("temperature_2m", 0.0)
            condition = WEATHER_CODES.get(code, "Unknown conditions")
            advice = advise_for_weather(temp, code)
            location = fetch_location_name(lat_f, lon_f)
            
            result = {
                "location": {
                    "name": location.get("name"),
                    "region": location.get("region"),
                    "country": location.get("country"),
                    "latitude": lat_f,
                    "longitude": lon_f
                },
                "current": {
                    "temperature": temp,
                    "apparent_temperature": current.get("apparent_temperature"),
                    "humidity": current.get("relative_humidity_2m"),
                    "wind_speed": current.get("wind_speed_10m"),
                    "condition_code": code,
                    "condition": condition,
                    "time": current.get("time")
                },
                "advice": advice
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            print(f"Weather data sent successfully", file=sys.stderr)
            
        except Exception as e:
            print(f"Weather error: {e}", file=sys.stderr)
            self.send_response(502)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unable to fetch weather data", "details": str(e)}).encode())
