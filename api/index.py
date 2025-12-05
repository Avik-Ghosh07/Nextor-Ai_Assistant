from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

app = Flask(__name__)
CORS(app)

# Import the handlers
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
gemini_model = None

if GEMINI_AVAILABLE and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-2.0-flash')
        print("✓ Gemini initialized", file=sys.stderr)
    except Exception as e:
        print(f"✗ Gemini failed: {e}", file=sys.stderr)

# Import the logic from other files
import importlib.util
import os

# Load chat functions
chat_spec = importlib.util.spec_from_file_location("chat_module", os.path.join(os.path.dirname(__file__), "chat.py"))
chat_module = importlib.util.module_from_spec(chat_spec)
chat_spec.loader.exec_module(chat_module)

# Load weather functions  
weather_spec = importlib.util.spec_from_file_location("weather_module", os.path.join(os.path.dirname(__file__), "weather.py"))
weather_module = importlib.util.module_from_spec(weather_spec)
weather_spec.loader.exec_module(weather_module)

@app.route('/api/health')
def health():
    return jsonify({
        "status": "ok",
        "gemini_available": GEMINI_AVAILABLE,
        "gemini_configured": bool(GEMINI_API_KEY)
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '').strip()
    history = data.get('history', [])
    
    if not message:
        return jsonify({"error": "Message is required"}), 400
    
    # Try Gemini first
    reply = chat_module.get_gemini_reply(message, history) if gemini_model else None
    
    # Fallback to pattern matching
    if not reply:
        reply = chat_module.get_fallback_reply(message)
    
    return jsonify({"reply": reply})

@app.route('/api/weather')
def weather():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    
    if not lat or not lon:
        return jsonify({"error": "Missing lat/lon"}), 400
    
    try:
        import requests
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&timezone=auto"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
