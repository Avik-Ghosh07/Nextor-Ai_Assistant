from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import datetime as dt
import random
import re
from typing import Dict, List

# Import Gemini AI (optional dependency)
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
    except Exception as e:
        print(f"⚠️ Gemini AI initialization failed: {e}", file=sys.stderr)

def get_gemini_reply(message: str, history: List[Dict[str, str]] = None) -> str | None:
    """Get reply from Gemini AI with conversation history."""
    if not gemini_model:
        return None
    
    try:
        # Build conversation context for Gemini
        context = "You are Nextor, a helpful AI voice assistant. You help with productivity, answer questions, provide motivation, and assist with daily tasks. Be friendly, concise, and helpful. Keep responses under 100 words unless asked for more detail.\n\n"
        
        # Add recent conversation history (last 6 messages)
        if history:
            recent = history[-6:]
            for item in recent:
                role = "User" if item.get("role") == "user" else "Assistant"
                msg = item.get("text", item.get("message", ""))
                context += f"{role}: {msg}\n"
        
        context += f"User: {message}\nAssistant:"
        
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
    
    # Greetings
    greeting_words = [r"\bhi\b", r"\bhello\b", r"\bhey\b"]
    if any(re.search(pattern, lowered) for pattern in greeting_words) and len(lowered.split()) <= 3:
        return random.choice([
            f"{greeting} I'm Nextor, your AI assistant. How can I help?",
            f"{greeting} Ready to assist you!",
            "Hello! What can I do for you today?"
        ])
    
    if "how are you" in lowered:
        return "I'm doing great! How can I help you today?"
    
    # Gratitude
    if "thank" in lowered:
        return random.choice(["You're welcome!", "Anytime!", "Happy to help!"])
    
    # Farewell
    if "bye" in lowered or "goodbye" in lowered:
        return random.choice(["Goodbye!", "See you later!", "Take care!"])
    
    # Motivation
    if "motivat" in lowered:
        return random.choice([
            "You've got this! Break the task into small steps and tackle them one at a time.",
            "Your future self will thank you for starting today!",
            "Progress, not perfection. Let's get started!"
        ])
    
    # Productivity
    if "productivity" in lowered or "productive" in lowered:
        return random.choice([
            "Try the Pomodoro Technique: 25 minutes of focused work, then a 5-minute break!",
            "Start your day by identifying your top 3 priorities.",
            "Eliminate distractions and create a dedicated workspace for maximum focus."
        ])
    
    # Weather
    if "weather" in lowered:
        return "I can fetch live weather for your location! Just enable location permissions and I'll give you temperature, conditions, and helpful advice!"
    
    # Default
    return "I'm here to help! Ask me anything or try commands like 'what's the weather'."

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Empty request body"}).encode())
                return
            
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            message = data.get('message', '').strip()
            history = data.get('history', [])
            
            if not message:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Message is required"}).encode())
                return
            
            reply = get_gemini_reply(message, history)
            if not reply:
                reply = get_fallback_reply(message)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"reply": reply}).encode())
            
        except Exception as e:
            print(f"Chat error: {e}", file=sys.stderr)
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Internal server error"}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
