# Nextor — AI Voice Assistant

> **A hands-free, browser-first AI assistant that understands natural speech and responds with human-like voice.**

Nextor is an interactive AI voice companion that runs locally or on the cloud, combining browser speech recognition with a powerful Python backend. Get real-time weather updates, set smart reminders with notifications, play music from YouTube, solve math problems, and chat naturally—all through voice commands.

**🎯 Perfect for:** Productivity enthusiasts, developers wanting a customizable AI assistant, anyone seeking hands-free task management.

**⚡ Tech Stack:** HTML5, Tailwind CSS, Vanilla JavaScript · Python Flask + Waitress · Google Gemini AI · Open-Meteo Weather API · Web Speech API

---

## ✨ Features

### 🎙️ Voice & AI
- ✅ **Voice Recognition & Speech Synthesis** - Hands-free interaction
- ✅ **AI-Powered Conversations** - Powered by Google Gemini 2.0 Flash
- ✅ **Pattern-Based Fallback** - Works without AI for basic commands
- ✅ **Custom Knowledge Teaching** - Train Nextor with your own responses

### 📋 Productivity
- ✅ **Smart Task Reminders** - Natural language parsing ("remind me in 10 minutes")
- ✅ **Multi-Alert Notifications** - Browser notifications + sound + vibration + visual alerts
- ✅ **Persistent Reminders** - Survive page refreshes and work on mobile
- ✅ **Background Reminder Watcher** - Checks every 10 seconds for due reminders

### 🌤️ Weather & Location
- ✅ **Live Weather Updates** - Real-time data from Open-Meteo API
- ✅ **Automatic Location Detection** - HTTPS-enabled geolocation
- ✅ **Weather Advice** - Context-aware suggestions based on conditions
- ✅ **Mobile-Optimized** - Device-specific error messages for iOS/Android

### 🎵 Entertainment & Utilities
- ✅ **Music Playback** - YouTube integration (Hindi, English, Bengali songs)
- ✅ **Math Calculations** - Instant voice-based calculator
- ✅ **Quick Commands** - Website navigation, searches, app launching
- ✅ **Motivational Quotes** - Productivity tips and inspiration

### 🎨 Design & UX
- ✅ **Fully Responsive** - Optimized for mobile, tablet, desktop, ultra-wide, 4K
- ✅ **Landscape Mode Support** - Special layouts for mobile/tablet landscape
- ✅ **Touch-Optimized** - 44px minimum touch targets, vibration feedback
- ✅ **Rich Conversation UI** - Timestamps, message history, glass morphism design
- ✅ **Local Persistence** - localStorage for reminders, knowledge, chat history

---

## 🚀 Deployment

### Deploy to Render (Recommended)
1. **Fork/Clone** this repository
2. **Go to** [render.com](https://render.com)
3. **Create New Web Service** → Connect GitHub repository
4. **Render auto-detects** `render.yaml` configuration
5. **Add Environment Variable:**
   - Key: `GEMINI_API_KEY`
   - Value: Your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
6. **Deploy!** - Your app will be live at `https://your-app.onrender.com`

**✅ Benefits:**
- Free HTTPS certificate (required for mobile geolocation)
- Auto-deploy on Git push
- Production-ready with Waitress WSGI server

---

## 🛠️ Local Development

### Requirements
- **Python 3.8+** (tested on Python 3.11)
- **Modern Browser** (Chrome, Edge, Safari with Web Speech API)
- **Internet Connection** (for weather API and Gemini AI)

### Quick Start
```bash
# 1. Clone the repository
git clone https://github.com/Avik-Ghosh07/Nextor-Ai_Assistant.git
cd Nextor-Ai_Assistant

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up Google Gemini AI (Optional but Recommended)
# Get free API key: https://makersuite.google.com/app/apikey
# Copy .env.example to .env
cp .env.example .env
# Edit .env and add: GEMINI_API_KEY=your_key_here

# 4. Start the server
python server.py

# Server will start at http://127.0.0.1:5000
```

**First Time Setup:**
1. Open http://127.0.0.1:5000 in your browser
2. **Allow microphone** access when prompted
3. **Allow notifications** for reminder alerts
4. **Allow location** for weather features
5. Click **"Activate Nextor"** and start talking!

**Note:** Nextor works without Gemini API using intelligent pattern-based responses as fallback.

---

## 📝 Voice Commands Examples

### 🎵 Music & Entertainment
```
"play a hindi song"
"play Shape of You"
"play some music"
"play bengali song"
```

### 🌤️ Weather
```
"what's the weather"
"weather update"
"how's the weather today"
```

### ⏰ Reminders
```
"remind me to call mom in 10 minutes"
"remind me to take medicine at 6:30pm"
"set a reminder for tomorrow at 8am"
"remind me in 1 hour"
```

### 🧮 Math & Utilities
```
"what is 5 plus 7"
"calculate 12 times 8"
"what time is it"
"flip a coin"
"roll a dice"
```

### 🌐 Navigation & Search
```
"open youtube"
"open github"
"open instagram"
"search for climate change"
"google python tutorial"
```

### 💪 Productivity & Motivation
```
"motivate me"
"give me productivity tips"
"how to focus better"
"I'm feeling stressed"
```

### 💬 Conversation
```
"hello"
"how are you"
"tell me a joke"
"thank you"
```

---

## 🎓 Teach Nextor Custom Responses

Use the **"Teach Nextor Something"** form in the interface:

**Format Examples:**
```
hello => Hi there, friend!
what's your favorite color => I love blue like the sky
good night => Sweet dreams! Sleep well and recharge
```

**Trigger phrases:**
- Simple keywords: `hello`, `bye`, `thanks`
- Questions: `what's your name`, `how old are you`
- Commands: `good morning`, `good night`

Next time you say the trigger phrase, Nextor responds with your custom answer!

---

## 🔧 Configuration & Customization

### Environment Variables
```bash
# .env file
GEMINI_API_KEY=your_google_gemini_api_key_here
PORT=5000  # Optional: Server port (auto-set by Render)
```

### Modify API Endpoint (if needed)
Edit `script.js` line 5-7:
```javascript
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://127.0.0.1:5000' 
    : '';  // Uses same domain in production
```

### Customizing Responses
Edit `server.py` function `_choose_reply()` to add your own response patterns.

---

## 💡 Tips & Troubleshooting

### 📱 Mobile Issues

**Location Not Working:**
- ✅ Ensure you're on **HTTPS** (Render provides this automatically)
- ✅ Enable location in browser settings
- ✅ **Important:** Close browser completely and reopen after enabling location
- 
**iOS:**
  - Settings > Safari > Location > While Using App
  - Settings > Privacy & Security > Location Services > Safari > While Using

**Android:**
  - Settings > Apps > Chrome > Permissions > Location > Allow
  - Enable GPS in Quick Settings

**Reminders Not Firing:**
- ✅ Allow notifications when prompted
- ✅ Keep browser tab open or in background
- ✅ Reminders check every 10 seconds
- ✅ Multiple alerts: notification + sound + vibration + visual popup

### 🖥️ Desktop Issues

**Voice Recognition Not Working:**
- ✅ Use Chrome, Edge, or Safari (Firefox has limited support)
- ✅ Check microphone permissions in browser settings
- ✅ Ensure you're on HTTPS or localhost

**Backend Not Connecting:**
- ✅ Check if server is running: `python server.py`
- ✅ Look for "Backend Online" status indicator (green)
- ✅ Check browser console for errors (F12)

### ⚙️ General Tips
- **Quiet Environment** - Better voice recognition accuracy
- **Clear Speech** - Speak naturally but clearly
- **Refresh Page** - If reminders seem stuck
- **Check Console** - Press F12 to see debug logs

---

## 🏗️ Project Structure

```
Nextor-Ai-Assistant/
├── index.html           # Main UI
├── script.js            # Frontend logic (1600+ lines)
├── style.css            # Responsive styles with glass morphism
├── server.py            # Flask backend with Gemini AI integration
├── requirements.txt     # Python dependencies
├── render.yaml          # Render deployment config
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

---

## 🌐 Tech Stack Details

### Frontend
- **HTML5** - Semantic markup
- **Tailwind CSS** - Utility-first styling
- **Vanilla JavaScript** - No frameworks, pure ES6+
- **Web Speech API** - Voice recognition & synthesis
- **LocalStorage** - Client-side persistence

### Backend
- **Python 3.11+** - Core runtime
- **Flask 2.3+** - Web framework
- **Waitress** - Production WSGI server
- **Flask-CORS** - Cross-origin support
- **Google Generative AI** - Gemini 2.0 Flash model
- **Requests** - HTTP client for APIs

### APIs & Services
- **Google Gemini AI** - Natural language understanding
- **Open-Meteo** - Weather data (free, no API key needed)
- **Web Speech API** - Browser-native voice features
- **YouTube** - Music playback

### Deployment
- **Render** - Cloud hosting with free HTTPS
- **Git** - Version control & auto-deploy

---

## 📊 Browser Compatibility

| Browser | Desktop | Mobile | Voice | Location |
|---------|---------|--------|-------|----------|
| Chrome  | ✅ Full | ✅ Full | ✅ | ✅ |
| Edge    | ✅ Full | ✅ Full | ✅ | ✅ |
| Safari  | ✅ Full | ✅ Full | ✅ | ✅ HTTPS only |
| Firefox | ⚠️ Limited | ⚠️ Limited | ❌ | ✅ |

**Note:** Firefox doesn't support Web Speech API for recognition. Use Chrome/Edge/Safari for best experience.

---

## 🔐 Privacy & Security

- ✅ **No data collection** - Everything runs in your browser/server
- ✅ **Local storage only** - Reminders and knowledge stored locally
- ✅ **Optional AI** - Works without Gemini API
- ✅ **HTTPS enforced** - Location requires secure connection
- ✅ **API key security** - Never exposed to client
- ✅ **Open source** - Audit the code yourself

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Created By

**Mr. Avik Ghosh**

GitHub: [@Avik-Ghosh07](https://github.com/Avik-Ghosh07)

---

## 🙏 Acknowledgments

- Google Gemini AI for intelligent conversations
- Open-Meteo for free weather data
- Vercel/Render for easy deployment
- Web Speech API community

---

## 🐛 Issues & Support

Found a bug or have a feature request?
- 📝 [Open an issue](https://github.com/Avik-Ghosh07/Nextor-Ai_Assistant/issues)
- 💬 Check existing issues first
- 🔍 Include browser/device info for bugs

---

**⭐ If you find this project helpful, please star it on GitHub!**

Made with ❤️ by Avik Ghosh
