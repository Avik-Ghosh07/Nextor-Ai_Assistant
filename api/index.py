from __future__ import annotations

import datetime as dt
import os
import random
import re
import sys
from typing import Any, Dict, List

import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# Import Gemini AI (optional dependency)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Create Flask app - static files are served by Vercel, not Flask
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure Gemini AI - use os.environ instead of dotenv for Vercel
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
gemini_model = None

print(f"GEMINI_API_KEY present: {bool(GEMINI_API_KEY)}", file=sys.stderr)
print(f"GEMINI_AVAILABLE: {GEMINI_AVAILABLE}", file=sys.stderr)

if GEMINI_AVAILABLE and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-2.0-flash')
        print("✅ Gemini AI initialized successfully", file=sys.stderr)
    except Exception as e:
        print(f"⚠️ Gemini AI initialization failed: {e}", file=sys.stderr)

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

def get_gemini_reply(message: str, history: List[Dict[str, str]] = None) -> str | None:
    """Get reply from Gemini AI with conversation history."""
    if not gemini_model:
        print("Gemini model not available", file=sys.stderr)
        return None
    
    try:
        context = f"User: {message}"
        if history:
            history_text = "\n".join([
                f"{h.get('role', 'User')}: {h.get('message', '')}" 
                for h in history[-5:]
            ])
            context = f"{history_text}\nUser: {message}"
        
        response = gemini_model.generate_content(context)
        
        if response and response.text:
            reply = response.text.strip()
            if reply.lower().startswith('nextor:'):
                reply = reply[7:].strip()
            return reply
        return None
        
    except Exception as e:
        print(f"Gemini error: {e}", file=sys.stderr)
        return None

def get_fallback_reply(message: str) -> str:
    """Pattern-based fallback responses."""
    lowered = message.lower()
    now = dt.datetime.now()
    greeting = f"Good {('morning' if now.hour < 12 else 'afternoon' if now.hour < 18 else 'evening')}!"
    
    greeting_words = ["\\bhi\\b", "\\bhello\\b", "\\bhey\\b"]
    if any(re.search(pattern, lowered) for pattern in greeting_words) and len(lowered.split()) <= 3:
        return random.choice([
            f"{greeting} I'm Nextor, your AI assistant. How can I help?",
            f"{greeting} Ready to assist you!",
            "Hello! What can I do for you today?"
        ])
    
    if "how are you" in lowered:
        return "I'm doing great! How can I help you today?"
    
    if "thank" in lowered:
        return random.choice(["You're welcome!", "Anytime!", "Happy to help!"])
    
    if "bye" in lowered or "goodbye" in lowered:
        return random.choice(["Goodbye!", "See you later!", "Take care!"])
    
    if "motivat" in lowered:
        return random.choice([
            "You've got this! Break the task into small steps and tackle them one at a time.",
            "Your future self will thank you for starting today!",
            "Progress, not perfection. Let's get started!"
        ])
    
    if "productivity" in lowered or "productive" in lowered:
        return random.choice([
            "Try the Pomodoro Technique: 25 minutes of focused work, then a 5-minute break!",
            "Start your day by identifying your top 3 priorities.",
            "Eliminate distractions and create a dedicated workspace for maximum focus."
        ])
    
    return "I'm here to help! Ask me anything or try commands like 'what's the weather'."

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

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "gemini_available": GEMINI_AVAILABLE,
        "gemini_configured": bool(GEMINI_API_KEY)
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint."""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        history = data.get('history', [])
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        reply = get_gemini_reply(message, history)
        if not reply:
            reply = get_fallback_reply(message)
        
        return jsonify({"reply": reply})
    except Exception as e:
        print(f"Chat error: {e}", file=sys.stderr)
        return jsonify({"error": "Internal server error"}), 500

@app.route('/weather')
def weather():
    """Weather endpoint."""
    try:
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        
        if not lat or not lon:
            return jsonify({"error": "Missing lat/lon parameters"}), 400
        
        lat, lon = float(lat), float(lon)
        
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
        
        return jsonify({
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
        })
    except Exception as e:
        print(f"Weather error: {e}", file=sys.stderr)
        return jsonify({"error": str(e)}), 500

# Vercel serverless function handler
handler = app
