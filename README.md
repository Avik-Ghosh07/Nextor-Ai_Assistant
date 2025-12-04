# Nextor — AI Voice Assistant

> **A hands-free, browser-first AI assistant that understands natural speech and responds with human-like voice.**

Nextor is an interactive AI voice companion that runs locally, blends browser speech recognition with a lightweight Python backend, and brings your daily workflows together in a polished interface. Get real-time weather updates, set task reminders, play music from YouTube, solve math on the fly, and chat naturally—all through voice commands.

**🎯 Perfect for:** Productivity enthusiasts, developers wanting a local AI assistant, anyone seeking hands-free task management.

**⚡ Tech Stack:** HTML5, Tailwind CSS, Vanilla JavaScript · Python Flask (Vercel serverless) · Open-Meteo Weather API · Web Speech API

---

## 📱 Features
- ✅ Voice Recognition & Speech Synthesis
- ✅ **AI-Powered Conversations** (Google Gemini - Optional)
- ✅ Live Weather Updates (Open-Meteo API)
- ✅ Task Reminders with Natural Language Parsing
- ✅ Music Playback (YouTube Integration)
- ✅ Math Calculations
- ✅ Quick Commands & Website Navigation
- ✅ Mobile Responsive Design
- ✅ Custom Knowledge Teaching
- ✅ Rich Conversation UI with Timestamps
- ✅ Local Persistence with localStorage

---

## 🛠️ Local Development

### Requirements
- Python 3.8+ (for local server)
- Modern browser (Chrome/Edge/Safari with Web Speech API support)
- Internet connection for weather API

### Run Locally
```bash
# Install dependencies
pip install -r requirements.txt

# (Optional) Set up Google Gemini AI for intelligent conversations
# 1. Get a free API key from https://makersuite.google.com/app/apikey
# 2. Copy .env.example to .env
# 3. Add your API key to .env: GEMINI_API_KEY=your_key_here

# Start server
python server.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser, grant microphone (and optionally notification/location) access, then tap **Activate Nextor** to start talking.

**Note:** Nextor works without Gemini API - it will use pattern-based responses as fallback.

---

## 📝 Voice Commands Examples

**Music:**
- "play a hindi song"
- "play Shape of You"

**Weather:**
- "what's the weather"
- "weather update"

**Math:**
- "5 plus 7"
- "what is 12 times 8"

**General:**
- "what time is it"
- "tell me a joke"
- "flip a coin"
- "remind me to call mom at 5 PM"
- "open youtube"
- "open github"
- "search for climate change solutions"
- "motivate me for work"
- "give me a productivity tip"

---

## 🎓 Teach Nextor Something New

Use the teach form underneath the conversation panel. Supported formats:
- `hello => Hi there!`
- `when I say good night, reply Sleep well and recharge`

Next time you say the trigger phrase, Nextor will respond with your custom answer.

---

## 💡 Notes & Tips

- Allow **notifications** to receive reminder pop-ups.
- Allow **location** when prompted to enable real-time weather for your current spot.
- Reminders persist in `localStorage` and re-schedule every time you reopen the page.
- If you change the backend port or host, update `API_BASE_URL` in `script.js`.
- For best results use a quiet environment and a Chromium-based browser.

### Reminder Time Formats
- `"remind me to call mom in 10 minutes"`
- `"remind me to check the oven at 6:30pm"`
- `"remind me to take pills tomorrow at 8am"`
- Parsed times after the current day roll over to the next logical slot (e.g. "at 3pm" after 3pm runs tomorrow).

---

## 🌐 Tech Stack
- **Frontend:** HTML5, Tailwind CSS, Vanilla JavaScript
- **Backend:** Python Flask (converted to Vercel Serverless Functions)
- **APIs:** Open-Meteo Weather API, Web Speech API
- **Deployment:** Vercel

---

## 👨‍💻 Created By
**Mister Avik Ghosh**

---

For issues or questions, feel free to open an issue on GitHub!
