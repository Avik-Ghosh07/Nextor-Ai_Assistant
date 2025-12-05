from http.server import BaseHTTPRequestHandler
import json
import random
import re
import os
import datetime as dt
import sys

# Import Gemini AI (optional dependency)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError as e:
    GEMINI_AVAILABLE = False
    print(f"Warning: google-generativeai not available: {e}", file=sys.stderr)

# Configure Gemini AI if API key is available
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
gemini_model = None

print(f"GEMINI_API_KEY present: {bool(GEMINI_API_KEY)}", file=sys.stderr)
print(f"GEMINI_AVAILABLE: {GEMINI_AVAILABLE}", file=sys.stderr)

if GEMINI_AVAILABLE and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-2.0-flash')
        print("✓ Gemini model initialized successfully", file=sys.stderr)
    except Exception as e:
        print(f"✗ Gemini initialization failed: {e}", file=sys.stderr)

def get_gemini_reply(message, history):
    """Get AI response from Gemini. Returns None if unavailable or fails."""
    if not gemini_model:
        print(f"Gemini not available - model: {gemini_model}, available: {GEMINI_AVAILABLE}, key: {bool(GEMINI_API_KEY)}", file=sys.stderr)
        return None
    
    try:
        # Build conversation context for Gemini
        context = "You are Nextor, a helpful AI voice assistant. You help with productivity, answer questions, provide motivation, and assist with daily tasks. Be friendly, concise, and helpful. Keep responses under 100 words unless asked for more detail.\\n\\n"
        
        # Add recent conversation history (last 6 messages)
        if history:
            recent = history[-6:]
            for item in recent:
                role = "User" if item["role"] == "user" else "Assistant"
                context += f"{role}: {item['text']}\\n"
        
        context += f"User: {message}\\nAssistant:"
        
        # Generate response with Gemini
        response = gemini_model.generate_content(context)
        
        if response and response.text:
            reply = response.text.strip()
            # Remove any "Nextor:" prefix if AI includes it
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
    
    # Greetings - use word boundaries to avoid false matches
    greeting_words = ["\\bhi\\b", "\\bhello\\b", "\\bhey\\b"]
    if any(re.search(pattern, lowered) for pattern in greeting_words) and len(lowered.split()) <= 3:
        return random.choice([
            f"{greeting} I'm Nextor, your AI assistant. How can I help?",
            f"{greeting} Ready to assist you!",
            "Hello! What can I do for you today?"
        ])
    
    # Common responses
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
    
    # Default
    return "I'm here to help! Ask me anything or try commands like 'play music', 'what's the weather', or 'set a reminder'."

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode()
        
        try:
            data = json.loads(body) if body else {}
            message = data.get('message', '').strip()
            history = data.get('history', [])
            
            if not message:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Message is required"}).encode())
                return
            
            # Try Gemini AI first
            reply = get_gemini_reply(message, history)
            
            # Fallback to pattern matching
            if not reply:
                reply = get_fallback_reply(message)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"reply": reply}).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

