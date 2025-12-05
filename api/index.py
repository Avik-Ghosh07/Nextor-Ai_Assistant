from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import random
import re
import datetime as dt

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

def get_gemini_reply(message, history=None):
    """Get reply from Gemini AI."""
    if not gemini_model:
        return None
    try:
        context = f"User: {message}"
        if history:
            history_text = "\n".join([f"{h.get('role', 'User')}: {h.get('message', '')}" for h in history[-5:]])
            context = f"{history_text}\nUser: {message}"
        
        response = gemini_model.generate_content(context)
        if response and response.text:
            reply = response.text.strip()
            if reply.lower().startswith('nextor:'):
                reply = reply[7:].strip()
            return reply
        return None
    except Exception:
        return None

def get_fallback_reply(message):
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
    
    return "I'm here to help! Ask me anything."

@app.route('/health')
@app.route('/')
def health():
    return jsonify({
        "status": "ok",
        "gemini_available": GEMINI_AVAILABLE,
        "gemini_configured": bool(GEMINI_API_KEY)
    })

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '').strip()
    history = data.get('history', [])
    
    if not message:
        return jsonify({"error": "Message is required"}), 400
    
    reply = get_gemini_reply(message, history)
    if not reply:
        reply = get_fallback_reply(message)
    
    return jsonify({"reply": reply})

@app.route('/weather')
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
