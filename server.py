import datetime as dt
import os
import random
import re
from typing import Dict, List

import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Import Gemini AI (optional dependency)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')

# Production-ready CORS configuration
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')
CORS(app, resources={
    r"/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "max_age": 3600
    }
})

# Security configurations
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024  # 16KB max request size
app.config['JSON_SORT_KEYS'] = False

# Rate limiting (simple in-memory tracker)
request_tracker = {}
RATE_LIMIT = int(os.getenv('RATE_LIMIT', '60'))  # requests per minute
RATE_WINDOW = 60  # seconds

def check_rate_limit(client_ip: str) -> bool:
    """Simple rate limiting check. Returns True if allowed."""
    now = dt.datetime.now().timestamp()
    if client_ip not in request_tracker:
        request_tracker[client_ip] = []
    
    # Remove old requests outside the window
    request_tracker[client_ip] = [
        req_time for req_time in request_tracker[client_ip]
        if now - req_time < RATE_WINDOW
    ]
    
    # Check if limit exceeded
    if len(request_tracker[client_ip]) >= RATE_LIMIT:
        return False
    
    request_tracker[client_ip].append(now)
    return True

# Configure Gemini AI if API key is available
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
gemini_model = None

if GEMINI_AVAILABLE and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        print("✅ Gemini AI initialized successfully (gemini-2.0-flash-exp)")
    except Exception as e:
        print(f"⚠️ Gemini AI initialization failed: {e}")
        print("ℹ️ App will use web search and built-in responses as fallback")
else:
    if not GEMINI_AVAILABLE:
        print("ℹ️ google-generativeai not installed. Using web search fallback.")
    if not GEMINI_API_KEY:
        print("ℹ️ GEMINI_API_KEY not set. Using web search and built-in responses.")

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODE_API_URL = "https://geocoding-api.open-meteo.com/v1/reverse"
DUCKDUCKGO_INSTANT_ANSWER_URL = "https://api.duckduckgo.com/"

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Rain showers",
    81: "Heavy rain showers",
    82: "Violent rain showers",
    85: "Snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def _safe_float(value) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _fetch_location_name(lat: float, lon: float) -> Dict[str, str]:
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


def _advise_for_weather(temp_c: float, condition_code: int) -> str:
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


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/weather")
def get_weather():
    try:
        # Rate limiting
        client_ip = request.remote_addr or 'unknown'
        if not check_rate_limit(client_ip):
            return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429
        
        lat = _safe_float(request.args.get("lat"))
        lon = _safe_float(request.args.get("lon"))

        if lat is None or lon is None:
            return jsonify({"error": "lat and lon parameters are required"}), 400
        
        # Validate coordinates
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return jsonify({"error": "Invalid coordinates"}), 400

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
        advice = _advise_for_weather(current.get("temperature_2m", 0.0), code)
        location = _fetch_location_name(lat, lon)

        return jsonify(
            {
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
        )
    except (requests.RequestException, ValueError) as exc:
        return jsonify({"error": "Unable to fetch weather data", "details": str(exc)}), 502


def _clean_message(message: str) -> str:
    return message.strip()


def _search_web(query: str) -> str | None:
    """Search the web using DuckDuckGo Instant Answer API. Returns summary or None."""
    try:
        print(f"🔍 Searching web for: {query}")
        params = {
            'q': query,
            'format': 'json',
            'no_html': 1,
            'skip_disambig': 1
        }
        
        response = requests.get(DUCKDUCKGO_INSTANT_ANSWER_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Try different answer fields in order of preference
        answer = None
        
        # Abstract (best for "what is" questions)
        if data.get('Abstract'):
            answer = data['Abstract']
            source = data.get('AbstractSource', 'web')
            print(f"✅ Found abstract from {source}")
        
        # Definition (for dictionary-like queries)
        elif data.get('Definition'):
            answer = data['Definition']
            source = data.get('DefinitionSource', 'web')
            print(f"✅ Found definition from {source}")
        
        # Answer (direct answers like calculations, conversions)
        elif data.get('Answer'):
            answer = data['Answer']
            print(f"✅ Found direct answer")
        
        # Related topics (fallback)
        elif data.get('RelatedTopics') and len(data['RelatedTopics']) > 0:
            first_topic = data['RelatedTopics'][0]
            if isinstance(first_topic, dict) and first_topic.get('Text'):
                answer = first_topic['Text']
                print(f"✅ Found related topic answer")
        
        if answer:
            # Clean up the answer
            answer = answer.strip()
            # Limit to reasonable length for voice
            if len(answer) > 500:
                answer = answer[:497] + "..."
            return answer
        
        print(f"⚠️ No instant answer found for: {query}")
        return None
        
    except Exception as e:
        print(f"❌ Web search error: {e}")
        return None


def _get_gemini_reply(message: str, history: List[Dict[str, str]]) -> str | None:
    """Get AI response from Gemini. Returns None if unavailable or fails."""
    if not gemini_model:
        print("⚠️ Gemini model not available")
        return None
    
    try:
        print(f"🤖 Sending to Gemini AI: {message}")
        # Build conversation context for Gemini
        context = "You are a knowledgeable AI assistant. Answer questions directly and accurately. Be concise but informative. If asked about technical topics, programming, science, history, or general knowledge, provide clear explanations. Keep responses under 150 words unless more detail is requested.\n\n"
        
        # Add recent conversation history (last 6 messages)
        if history:
            recent = history[-6:]
            for item in recent:
                role = "User" if item["role"] == "user" else "Assistant"
                context += f"{role}: {item['text']}\n"
        
        context += f"User: {message}\nAssistant:"
        
        # Generate response with Gemini
        response = gemini_model.generate_content(context)
        
        if response and response.text:
            reply = response.text.strip()
            # Remove any "Nextor:" or "Assistant:" prefix if AI includes it
            if reply.lower().startswith('nextor:'):
                reply = reply[7:].strip()
            elif reply.lower().startswith('assistant:'):
                reply = reply[10:].strip()
            print(f"✅ Gemini replied: {reply[:100]}...")
            return reply
        return None
        
    except Exception as e:
        print(f"❌ Gemini AI error: {e}")
        return None


def _choose_reply(message: str, history: List[Dict[str, str]]) -> str:
    """Generate reply using Gemini AI, web search, or fallback to pattern matching."""
    
    # Try Gemini AI first
    gemini_reply = _get_gemini_reply(message, history)
    if gemini_reply:
        return gemini_reply
    
    # If Gemini fails, try web search for question-like queries
    lowered = message.lower()
    is_question = any(lowered.startswith(q) for q in ['what is', 'what are', 'who is', 'who are', 'when was', 'where is', 'how does', 'why does', 'define', 'explain', 'tell me about'])
    
    if is_question:
        web_answer = _search_web(message)
        if web_answer:
            print(f"✅ Using web search answer")
            return web_answer
    
    # Fallback to pattern-based responses
    print(f"⚠️ Gemini and web search unavailable, using fallback for: {message}")
    now = dt.datetime.now()
    greeting = f"Good {('morning' if now.hour < 12 else 'afternoon' if now.hour < 18 else 'evening')}!"

    # Greetings and basic interaction - use word boundaries to avoid false matches
    greeting_words = ["\bhi\b", "\bhello\b", "\bhey\b"]
    if any(re.search(pattern, lowered) for pattern in greeting_words) and len(lowered.split()) <= 3:
        greetings = [
            f"{greeting} I'm Nextor, your AI voice assistant. I can help with productivity tips, music, weather, reminders, calculations, and much more. What can I do for you today?",
            f"{greeting} Great to hear from you! I'm here to assist with tasks, answer questions, play music, check weather, and boost your productivity. How can I help?",
            f"{greeting} I'm Nextor, ready to assist! Try asking me about the weather, productivity tips, or say 'play a song'. What would you like?"
        ]
        return random.choice(greetings)

    if "how are you" in lowered or "how're you" in lowered:
        return "I'm functioning perfectly and ready to help you achieve great things today! How are you feeling? Is there anything I can assist you with?"

    # Music and entertainment
    if "play" in lowered and ("song" in lowered or "music" in lowered):
        if "hindi" in lowered:
            return "Great choice! I'll play a random popular Hindi song for you on YouTube. Enjoy the music!"
        elif "bengali" in lowered or "bangla" in lowered:
            return "Wonderful! I'll play a random Bengali song for you on YouTube. Get ready to enjoy some great music!"
        elif "english" in lowered:
            return "Perfect! I'll play a random popular English song for you on YouTube. Enjoy!"
        return "I can play Hindi, Bengali, or English songs for you! Just specify the language, or I'll pick a great Hindi song. Enjoy!"

    # Productivity and motivation
    if "motivat" in lowered or "motivation" in lowered or "inspire" in lowered:
        motivational_quotes = [
            "You've got this! Break the task into one focused step, get that done, and the momentum will follow. Small wins lead to big victories. What would you like to tackle first?",
            "Your future self will thank you for getting started today. Every expert was once a beginner who refused to give up. Let's take the first step together!",
            "Progress, not perfection. Focus on doing one thing well right now, and build from there. You have everything you need to succeed!",
            "Remember: the best time to start was yesterday, the second best time is now. Don't wait for perfect conditions - create them! Let's make today count!",
            "Success is the sum of small efforts repeated day in and day out. You're already making progress by being here. Keep going!"
        ]
        return random.choice(motivational_quotes)

    if "stress" in lowered or "overwhelm" in lowered or "stressed" in lowered or "anxious" in lowered:
        return (
            "I hear you - stress happens to everyone. Let's tackle this together. Here's what helps: "
            "1) Take 3 deep breaths right now, 2) Write down your top 2 priorities only, "
            "3) Set a timer for 25 minutes and focus on just one task, 4) Take a 5-minute break after. "
            "You're stronger than you think. I'm here to support you!"
        )

    if "productivity" in lowered or "productive" in lowered or "efficient" in lowered or "focus" in lowered:
        productivity_tips = [
            "Try the Pomodoro Technique: 25 minutes of deep focused work, then a 5-minute break. After 4 rounds, take a longer 15-30 minute break. This prevents burnout and maintains peak performance.",
            "Start your day by identifying your top 3 priorities. Focus on completing these before anything else - they're your non-negotiables. Everything else can wait.",
            "Eliminate distractions: turn off notifications, close unnecessary tabs, put your phone on silent, and create a dedicated workspace. Your brain will thank you!",
            "Use the 2-minute rule: if a task takes less than 2 minutes, do it immediately. This prevents small tasks from piling up and overwhelming you later.",
            "Batch similar tasks together. Group all your emails, phone calls, and meetings. This reduces context switching and dramatically improves focus and efficiency."
        ]
        return random.choice(productivity_tips)

    # Gratitude
    if "thank" in lowered or "thanks" in lowered or "appreciate" in lowered:
        thanks_responses = [
            "You're very welcome! I'm always here to help. Is there anything else you'd like assistance with?",
            "My pleasure! That's what I'm here for. Feel free to ask me anything anytime!",
            "You're welcome! Happy to help. What else can I do for you today?"
        ]
        return random.choice(thanks_responses)

    # Weather
    if "weather" in lowered:
        return (
            "I can fetch live weather for your location! Just say 'what's the weather' or click the refresh button "
            "in the weather panel. Make sure to grant location permission when your browser asks. "
            "I'll give you temperature, conditions, humidity, wind speed, and helpful advice!"
        )

    # Jokes and entertainment
    if "joke" in lowered or "funny" in lowered or "laugh" in lowered:
        jokes_list = [
            "Why don't programmers trust stairs? Because they're always up to something!",
            "Why did the developer go broke? Because they used up all their cache!",
            "Parallel lines have so much in common. It's a shame they'll never meet.",
            "I tried to catch fog yesterday. Mist!",
            "Why do Java developers wear glasses? Because they can't C sharp!",
            "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?'",
            "Why did the computer go to therapy? It had too many bytes of emotional baggage!",
            "How many programmers does it take to change a light bulb? None, that's a hardware problem!"
        ]
        return random.choice(jokes_list)

    # Planning and organization
    if "plan" in lowered or "schedule" in lowered or "organize" in lowered:
        planning_advice = [
            "Let's create a solid plan! Start by identifying your main goal, then break it into smaller, achievable steps. What's the main outcome you want to accomplish?",
            "Here's a proven planning framework: 1) Define your goal with crystal clarity, 2) List all necessary steps, 3) Prioritize by importance and urgency, 4) Set realistic deadlines. What would you like to plan?",
            "Effective planning starts with absolute clarity. Ask yourself: What exactly do I want to accomplish? Why is it important? What resources do I need? When do I want to complete it? Let's start with your main objective!"
        ]
        return random.choice(planning_advice)

    # Time management
    if "time management" in lowered or "manage time" in lowered or "time" in lowered and "manage" in lowered:
        return (
            "Excellent! Here are powerful time management strategies: "
            "1) Use time blocking - schedule specific blocks for specific tasks, "
            "2) Apply the Eisenhower Matrix - prioritize by urgent vs important, "
            "3) Set strict time limits for each task to maintain focus, "
            "4) Review and adjust daily. "
            "Would you like me to help you create a time-blocked schedule for today?"
        )

    # Focus and concentration
    if "focus" in lowered or "concentrate" in lowered or "distracted" in lowered or "concentration" in lowered:
        return (
            "Let's boost your focus! Here's what works: "
            "1) Remove ALL distractions - phone on silent, close extra tabs, "
            "2) Use the Pomodoro Technique - 25 min work, 5 min break, "
            "3) Create a dedicated, clean workspace, "
            "4) Try 2 minutes of deep breathing before starting, "
            "5) Take movement breaks every hour. "
            "Ready to try a 25-minute focus session? Say 'remind me in 25 minutes'!"
        )

    # Goals and objectives
    if "goal" in lowered or "objective" in lowered or "achieve" in lowered or "target" in lowered:
        return (
            "Setting clear goals is crucial for success! Use the SMART framework: "
            "Specific, Measurable, Achievable, Relevant, and Time-bound. "
            "What goal would you like to work on? I can help you break it down into actionable steps."
        )

    # General helpful response (removed confusing context awareness)
    helpful_responses = [
        "I'm here to help you be more productive and efficient! I can assist with: productivity tips, playing music, answering questions, setting reminders, planning your day, and much more. What would you like to do?",
        "I'm Nextor, your AI productivity assistant! I can help you with time management, motivation, planning, playing music, answering questions, and staying organized. How can I assist you today?",
        "I'm listening and ready to help! Whether you need productivity advice, want to play music, set reminders, get answers to questions, or plan your day—I'm here for you. What can I do?"
    ]
    return random.choice(helpful_responses)


@app.post("/api/chat")
def chat():
    try:
        # Rate limiting
        client_ip = request.remote_addr or 'unknown'
        if not check_rate_limit(client_ip):
            return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429
        
        # Input validation
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400
        
        message = _clean_message(str(data.get("message", "")))
        if not message or len(message) > 1000:
            return jsonify({"error": "Message must be between 1 and 1000 characters"}), 400
        
        history = data.get("history") or []
        if not isinstance(history, list):
            history = []
        
        # Limit history size
        history = history[-10:] if len(history) > 10 else history
        
        # Get reply
        reply = _choose_reply(message, history)
        return jsonify({"reply": reply})
        
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.get("/api/health")
def health():
    return jsonify({
        "status": "healthy",
        "gemini_available": gemini_model is not None,
        "timestamp": dt.datetime.now().isoformat()
    })


if __name__ == "__main__":
    # Get port from environment variable (for Render, Heroku, etc.) or default to 5000
    port = int(os.environ.get("PORT", 5000))
    
    # Use Waitress for production-grade WSGI server
    try:
        from waitress import serve
        print("🚀 Starting Nextor AI with Waitress server...")
        print(f"📡 Server running on port {port}")
        print("🌐 Also accessible at http://0.0.0.0:" + str(port))
        print("Press Ctrl+C to stop the server")
        serve(app, host="0.0.0.0", port=port, threads=6)
    except ImportError:
        print("⚠️  Waitress not installed. Using Flask development server...")
        print("💡 Install Waitress for better performance: pip install waitress")
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False, threaded=True)


