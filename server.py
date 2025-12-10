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
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XSS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection

# Add security headers to all responses
@app.after_request
def add_security_headers(response):
    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
        "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://api.open-meteo.com https://geocoding-api.open-meteo.com; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )
    # Additional security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(self), microphone=(self), camera=()'
    return response

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
    """Sanitize message input to prevent XSS and injection attacks."""
    # Remove any HTML tags
    message = re.sub(r'<[^>]+>', '', message)
    # Remove script tags and event handlers
    message = re.sub(r'on\w+\s*=', '', message, flags=re.IGNORECASE)
    # Remove javascript: protocol
    message = re.sub(r'javascript:', '', message, flags=re.IGNORECASE)
    # Remove data: protocol
    message = re.sub(r'data:', '', message, flags=re.IGNORECASE)
    # Limit to printable ASCII and common Unicode
    message = ''.join(char for char in message if char.isprintable() or char.isspace())
    return message.strip()


def _search_web(query: str) -> str | None:
    """Search the web using Wikipedia API for factual queries, fallback to Google scraping."""
    try:
        print(f"🔍 Searching web for: {query}")
        
        # First try Wikipedia API for factual queries (works great for "who is", "what is")
        try:
            # Extract the subject from the query
            search_term = query.lower()
            search_term = search_term.replace('who is ', '').replace('who are ', '')
            search_term = search_term.replace('what is ', '').replace('what are ', '')
            search_term = search_term.replace('where is ', '').replace('where are ', '')
            search_term = search_term.replace('when was ', '').replace('when is ', '')
            search_term = search_term.strip()
            
            # Common name mappings
            name_mappings = {
                'amazon forest': 'Amazon rainforest',
                'amazon jungle': 'Amazon rainforest',
                'amazon': 'Amazon rainforest',
            }
            
            # Use mapped name if available
            wiki_title = name_mappings.get(search_term, search_term)
            
            wiki_url = "https://en.wikipedia.org/w/api.php"
            wiki_params = {
                'action': 'query',
                'format': 'json',
                'prop': 'extracts',
                'exintro': True,
                'explaintext': True,
                'redirects': 1,
                'titles': wiki_title
            }
            
            # Wikipedia requires User-Agent header
            headers = {
                'User-Agent': 'NextorAI/1.0 (Educational Project; Python/requests)'
            }
            
            wiki_response = requests.get(wiki_url, params=wiki_params, headers=headers, timeout=5)
            wiki_response.raise_for_status()
            wiki_data = wiki_response.json()
            
            pages = wiki_data.get('query', {}).get('pages', {})
            for page_id, page in pages.items():
                if page_id != '-1' and 'extract' in page:
                    extract = page['extract'].strip()
                    if extract and len(extract) > 50:
                        # Limit to first 2-3 sentences
                        sentences = extract.split('. ')[:3]
                        answer = '. '.join(sentences)
                        if not answer.endswith('.'):
                            answer += '.'
                        # Limit length
                        if len(answer) > 500:
                            answer = answer[:497] + "..."
                        print(f"✅ Found Wikipedia answer")
                        return answer
        except Exception as wiki_error:
            print(f"⚠️ Wikipedia search failed: {wiki_error}")
        
        # Fallback to Google search scraping
        print(f"🔍 Trying Google search...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
        response = requests.get(search_url, headers=headers, timeout=5)
        response.raise_for_status()
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try multiple selectors
        answer = None
        
        # Featured snippet
        for selector in ['div.hgKElc', 'span.hgKElc', 'div.IZ6rdc', 'span.aCOpRe']:
            element = soup.find(class_=selector.split('.')[-1])
            if element:
                answer = element.get_text(strip=True)
                print(f"✅ Found Google answer with selector: {selector}")
                break
        
        if answer:
            answer = answer.strip().replace('Wikipedia', '').strip()
            if len(answer) > 500:
                answer = answer[:497] + "..."
            return answer
        
        print(f"⚠️ No web answer found for: {query}")
        return None
        
    except ImportError:
        print(f"❌ BeautifulSoup not installed")
        return None
    except Exception as e:
        print(f"❌ Web search error: {e}")
        return None


def _get_gemini_reply(message: str, history: List[Dict[str, str]]) -> str | None:
    """Get AI response from Gemini with timeout. Returns None if unavailable or fails."""
    if not gemini_model:
        print("⚠️ Gemini model not available - Check GEMINI_API_KEY in .env file")
        return None
    
    try:
        print(f"🤖 Sending to Gemini AI: {message}")
        # Build conversation context for Gemini (minimal for speed)
        context = "You are Nextor, an AI assistant. Answer directly and concisely in under 100 words. Be helpful and accurate.\n\n"
        
        # Add only last 2 messages for faster processing
        if history:
            recent = history[-2:]
            for item in recent:
                role = "User" if item["role"] == "user" else "Assistant"
                context += f"{role}: {item['text']}\n"
        
        context += f"User: {message}\nAssistant:"
        
        # Generate response with Gemini (optimized for speed)
        generation_config = {
            "temperature": 0.7,
            "max_output_tokens": 150,  # Reduced for faster replies
            "top_p": 0.95,
            "top_k": 40
        }
        response = gemini_model.generate_content(
            context,
            generation_config=generation_config,
            request_options={"timeout": 3}  # 3 second timeout for speed
        )
        
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
        print(f"❌ Gemini AI error (using fallback): {e}")
        return None


def _get_builtin_knowledge(query: str) -> str | None:
    """Return built-in knowledge for common technical topics."""
    query_lower = query.lower()
    
    # Technical knowledge base
    knowledge_base = {
        'next js': "Next.js is a powerful React framework for building production-ready web applications. It provides features like server-side rendering, static site generation, API routes, and automatic code splitting. Created by Vercel, it's popular for building fast, SEO-friendly websites.",
        'nextjs': "Next.js is a powerful React framework for building production-ready web applications. It provides features like server-side rendering, static site generation, API routes, and automatic code splitting. Created by Vercel, it's popular for building fast, SEO-friendly websites.",
        'react': "React is a JavaScript library for building user interfaces, developed by Facebook. It uses a component-based architecture and virtual DOM for efficient rendering. React is widely used for creating interactive, single-page applications.",
        'react js': "React is a JavaScript library for building user interfaces, developed by Facebook. It uses a component-based architecture and virtual DOM for efficient rendering. React is widely used for creating interactive, single-page applications.",
        'vue': "Vue.js is a progressive JavaScript framework for building user interfaces. It's known for being easy to learn while powerful enough for complex applications. Vue uses a reactive data binding system and component-based architecture.",
        'vue js': "Vue.js is a progressive JavaScript framework for building user interfaces. It's known for being easy to learn while powerful enough for complex applications. Vue uses a reactive data binding system and component-based architecture.",
        'angular': "Angular is a TypeScript-based web application framework developed by Google. It's used for building dynamic single-page applications with a comprehensive set of tools including dependency injection, routing, and forms.",
        'node': "Node.js is a JavaScript runtime built on Chrome's V8 engine. It allows developers to run JavaScript on the server side, enabling full-stack JavaScript development and building scalable network applications.",
        'nodejs': "Node.js is a JavaScript runtime built on Chrome's V8 engine. It allows developers to run JavaScript on the server side, enabling full-stack JavaScript development and building scalable network applications.",
        'node js': "Node.js is a JavaScript runtime built on Chrome's V8 engine. It allows developers to run JavaScript on the server side, enabling full-stack JavaScript development and building scalable network applications.",
        'python': "Python is a high-level, general-purpose programming language known for its simple syntax and readability. It's widely used in web development, data science, artificial intelligence, automation, and scientific computing.",
        'javascript': "JavaScript is a versatile programming language primarily used for web development. It enables interactive features on websites and runs in browsers. It's also used server-side with Node.js and for mobile app development.",
        'typescript': "TypeScript is a superset of JavaScript that adds static typing. Developed by Microsoft, it helps catch errors early in development and improves code quality and maintainability in large-scale applications.",
        'html': "HTML (HyperText Markup Language) is the standard markup language for creating web pages. It defines the structure and content of websites using elements and tags like headings, paragraphs, links, and images.",
        'css': "CSS (Cascading Style Sheets) is used to style and layout web pages. It controls colors, fonts, spacing, and responsive design to make websites visually appealing and work across different screen sizes.",
        'tailwind': "Tailwind CSS is a utility-first CSS framework that provides low-level utility classes to build custom designs. It's popular for rapid UI development and creating responsive, modern interfaces without writing custom CSS.",
        'tailwind css': "Tailwind CSS is a utility-first CSS framework that provides low-level utility classes to build custom designs. It's popular for rapid UI development and creating responsive, modern interfaces without writing custom CSS.",
        'express': "Express.js is a minimal and flexible Node.js web application framework. It provides robust features for building web and mobile applications and APIs, making it one of the most popular backend frameworks.",
        'express js': "Express.js is a minimal and flexible Node.js web application framework. It provides robust features for building web and mobile applications and APIs, making it one of the most popular backend frameworks.",
        'mongodb': "MongoDB is a NoSQL document database that stores data in flexible, JSON-like documents. It's popular for modern applications that need to handle large amounts of unstructured data with high scalability.",
        'mern': "MERN stack is a popular JavaScript technology stack consisting of MongoDB (database), Express.js (backend framework), React (frontend library), and Node.js (runtime environment). It allows developers to build full-stack web applications using only JavaScript.",
        'mern stack': "The MERN stack includes MongoDB for the database, Express.js for the backend framework, React for the frontend, and Node.js as the runtime environment. It's a complete JavaScript solution for full-stack web development.",
        'mean': "MEAN stack consists of MongoDB, Express.js, Angular, and Node.js. Similar to MERN but uses Angular instead of React for the frontend framework.",
        'mean stack': "The MEAN stack includes MongoDB for the database, Express.js for the backend framework, Angular for the frontend, and Node.js as the runtime environment.",
        'sql': "SQL (Structured Query Language) is used to manage and manipulate relational databases. It allows you to create, read, update, and delete data efficiently in databases like MySQL, PostgreSQL, and SQL Server.",
        'git': "Git is a distributed version control system used to track changes in source code during software development. It helps developers collaborate, manage different versions of projects, and maintain code history.",
        'github': "GitHub is a web-based platform for version control using Git. It provides hosting for software development and enables collaboration, code sharing, project management, and open-source contribution.",
        'docker': "Docker is a platform for developing, shipping, and running applications in containers. Containers package software with all its dependencies, ensuring it runs consistently across different environments.",
        'kubernetes': "Kubernetes is an open-source container orchestration platform. It automates deployment, scaling, and management of containerized applications across clusters of hosts, making it easier to manage complex deployments.",
        'api': "API (Application Programming Interface) is a set of rules that allows different software applications to communicate with each other. It enables data exchange and functionality sharing between systems.",
        'rest api': "REST API is an architectural style for designing networked applications. It uses HTTP methods like GET, POST, PUT, and DELETE to perform operations on resources, making it easy to build web services.",
        'graphql': "GraphQL is a query language for APIs developed by Facebook. It allows clients to request exactly the data they need, reducing over-fetching and under-fetching compared to traditional REST APIs.",
        'aws': "AWS (Amazon Web Services) is a comprehensive cloud computing platform offering over 200 services including computing power, storage, and databases. It's the most widely used cloud provider.",
        'machine learning': "Machine learning is a subset of artificial intelligence where computers learn from data without being explicitly programmed. It powers applications like recommendation systems, image recognition, and predictive analytics.",
        'ai': "Artificial Intelligence is the simulation of human intelligence by machines. It includes learning, reasoning, and self-correction, and is used in applications like virtual assistants, autonomous vehicles, and data analysis.",
        'artificial intelligence': "Artificial Intelligence refers to computer systems that can perform tasks requiring human intelligence, such as visual perception, speech recognition, decision-making, and language translation.",
    }
    
    # Check for exact matches with word boundaries to avoid false positives
    # e.g., 'ai' shouldn't match 'Pichai', 'react' shouldn't match 'create'
    for keyword, answer in knowledge_base.items():
        # Use word boundaries for single words, exact match for multi-word phrases
        if ' ' in keyword:
            # Multi-word phrase - exact match
            if keyword in query_lower:
                print(f"✅ Using built-in knowledge for: {keyword}")
                return answer
        else:
            # Single word - use word boundaries
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, query_lower):
                print(f"✅ Using built-in knowledge for: {keyword}")
                return answer
    
    return None


def _choose_reply(message: str, history: List[Dict[str, str]]) -> str:
    """Generate reply using Gemini AI, web search, or fallback to pattern matching."""
    
    lowered = message.lower()
    
    # Check for built-in commands/patterns FIRST (before AI)
    # This ensures productivity tips, quotes, etc. are handled directly
    if any(keyword in lowered for keyword in ['productivity tip', 'productivity', 'productive', 'give me a tip', 'give me a productivity tip', 'tell me some productivity tips', 'some productivity tips', 'tips for productivity']):
        tips = [
            "Try the Pomodoro Technique: 25 minutes of deep focused work, then a 5-minute break. After 4 rounds, take a longer 15-30 minute break.",
            "Start your day by identifying your top 3 priorities. Focus on completing these before anything else - they're your non-negotiables.",
            "Eliminate distractions: turn off notifications, close unnecessary tabs, put your phone on silent, and create a dedicated workspace.",
            "Use the 2-minute rule: if a task takes less than 2 minutes, do it immediately. This prevents small tasks from piling up.",
            "Batch similar tasks together. Group all your emails, phone calls, and meetings to reduce context switching.",
            "Take regular breaks - your brain needs rest to maintain peak performance. Stand up, stretch, or take a short walk every hour.",
            "Use time blocking - schedule specific time slots for different tasks. This creates structure and helps you stay focused.",
            "Start with your most important task first thing in the morning when your energy is highest. Don't check emails or social media first."
        ]
        return random.choice(tips)
    
    if any(keyword in lowered for keyword in ['motivate me', 'motivation', 'inspire', 'quote', 'motivational quote', 'tell me some motivation', 'give me some motivational quote', 'give me some motivation']):
        quotes = [
            "You've got this! Break the task into one focused step, get that done, and the momentum will follow. Small wins lead to big victories.",
            "Your future self will thank you for getting started today. Every expert was once a beginner who refused to give up.",
            "Progress, not perfection. Focus on doing one thing well right now, and build from there. You have everything you need to succeed!",
            "The best time to start was yesterday, the second best time is now. Don't wait for perfect conditions - create them!",
            "Success is the sum of small efforts repeated day in and day out. You're already making progress by being here.",
            "Don't wait for motivation - start anyway. Action creates momentum, and momentum creates motivation.",
            "Every expert was once a beginner. Every master was once a disaster. Keep going, you're doing better than you think!",
            "Your only limit is you. Believe in yourself and you're halfway there. Now take the first step!"
        ]
        return random.choice(quotes)
    
    # Try Gemini AI FIRST for all messages
    # BUT check built-in knowledge for common tech questions first to save API quota
    # Skip built-in knowledge for "who is" questions (about people)
    is_question = any(lowered.startswith(q) for q in ['what is', 'what are', 'who is', 'who are', 'when was', 'where is', 'how does', 'why does', 'define', 'explain', 'tell me about','what was'])
    is_person_question = lowered.startswith('who is') or lowered.startswith('who are')
    
    if is_question and not is_person_question:
        # Try built-in knowledge first for common TECHNICAL topics (not people)
        builtin_answer = _get_builtin_knowledge(message)
        if builtin_answer:
            print(f"✅ Using built-in knowledge base")
            return builtin_answer
    
    # Try Gemini AI for other questions
    gemini_reply = _get_gemini_reply(message, history)
    if gemini_reply:
        return gemini_reply
    
    # If Gemini fails, try web search for ALL questions (not just specific patterns)
    if is_question:
        # Try web search for any question
        web_answer = _search_web(message)
        if web_answer:
            print(f"✅ Using web search answer")
            return web_answer
        else:
            print(f"⚠️ Web search returned no results for: {message}")
    
    # For non-question messages when Gemini fails, also try web search
    if not is_question:
        # Try web search for any conversational query
        web_answer = _search_web(message)
        if web_answer:
            print(f"✅ Using web search for conversational query")
            return web_answer
        else:
            print(f"⚠️ Web search returned no results for: {message}")
    
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

    # Stress and wellness (additional patterns)
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

    # General helpful response - but if it's a question that failed, indicate we couldn't answer
    if is_question:
        return f"I apologize, but I couldn't find information about '{message}'. My AI quota is currently exceeded and the web search didn't return results. Please try again later or rephrase your question."
    
    # For non-questions, provide general helpful response
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
        
        # Strict validation
        if not message:
            return jsonify({"error": "Message cannot be empty"}), 400
        if len(message) > 1000:
            return jsonify({"error": "Message too long (max 1000 characters)"}), 400
        if len(message) < 1:
            return jsonify({"error": "Message too short"}), 400
        
        # Validate message doesn't contain suspicious patterns
        suspicious_patterns = [r'<script', r'javascript:', r'onerror=', r'onclick=', r'eval\(']
        for pattern in suspicious_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return jsonify({"error": "Invalid message content"}), 400
        
        history = data.get("history") or []
        if not isinstance(history, list):
            history = []
        
        # Validate history items
        validated_history = []
        for item in history[-10:]:  # Limit to last 10
            if isinstance(item, dict) and 'role' in item and 'text' in item:
                if item['role'] in ['user', 'assistant']:
                    validated_history.append({
                        'role': item['role'],
                        'text': _clean_message(str(item['text']))[:500]  # Limit history text
                    })
        
        history = validated_history
        
        # Get reply
        reply = _choose_reply(message, history)
        return jsonify({"reply": reply})
        
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.get("/api/health")
def health():
    """Health check endpoint with minimal information disclosure."""
    return jsonify({
        "status": "healthy",
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat()
    }), 200


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


