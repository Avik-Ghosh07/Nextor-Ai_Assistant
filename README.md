# Nextor — AI Voice Assistant

> **A hands-free AI assistant that understands natural speech and responds with human-like voice.**

Interactive voice companion combining browser speech recognition with Python Flask backend. Get weather updates, set smart reminders, play music, solve math, and chat naturally—all through voice commands.

**⚡ Tech Stack:** HTML5 · JavaScript · Python Flask · Google Gemini AI · Web Speech API

---

## 🎯 Highlights

✨ **Zero Setup** - No installations, just open and talk  
🚀 **Deploy in 2 Minutes** - One-click Render deployment  
📱 **Mobile First** - Works perfectly on phones with haptic feedback  
🔒 **Privacy Focused** - All data stays local, no tracking  
🎨 **Beautiful UI** - Glass morphism design with smooth animations  
🧠 **Smart AI** - Gemini-powered or pattern-based fallback

---

## ✨ Features

- 🎙️ **Voice Recognition & AI Chat** - Powered by Google Gemini 2.0 Flash (optional)
- 📋 **Smart Reminders** - Natural language parsing with multi-modal alerts (sound + vibration + notifications)
- 🌤️ **Live Weather** - Auto-location detection with real-time updates
- 🎵 **Music & Entertainment** - YouTube playback, math calculator, quick commands
- 📱 **Fully Responsive** - Optimized for all devices from mobile to 4K
- 💾 **Local Persistence** - Reminders and chat history survive page refreshes

---

## 🚀 Quick Start

### Deploy to Render (Free)
1. Fork this repo → Go to [render.com](https://render.com) → Create Web Service
2. Connect GitHub → Render auto-detects `render.yaml`
3. Add environment variable: `GEMINI_API_KEY` (get from [Google AI Studio](https://makersuite.google.com/app/apikey))
4. Deploy! Live at `https://your-app.onrender.com`

### Run Locally
```bash
git clone https://github.com/Avik-Ghosh07/Nextor-Ai_Assistant.git
cd Nextor-Ai_Assistant
pip install -r requirements.txt
python server.py
```
Open http://127.0.0.1:5000 → Allow microphone/notifications/location → Click "Activate Nextor"

**Note:** Works without Gemini API using pattern-based fallback responses.

---

## 🎤 Voice Commands

**Music & Entertainment:**
```
"play a hindi song" | "play Shape of You"
```

**Weather & Time:**
```
"what's the weather" | "what time is it"
```

**Reminders:**
```
"remind me to call mom in 10 minutes"
"remind me to take medicine at 6:30pm"
```

**Math & Utilities:**
```
"what is 5 plus 7" | "flip a coin"
```

**Navigation:**
```
"open youtube" | "search for climate change"
```

**Productivity & Life Advice:**
```
"motivate me" | "give me productivity tips"
"work life balance advice" | "study tips"
"career advice" | "tell me a joke"
```

---

### 🎓 Teach Custom Responses

Use the teach form in the UI:
```
hello => Hi there, friend!
good night => Sweet dreams!
```

---

## 🔧 Troubleshooting

### 📱 Mobile Location Issues
- ✅ Must use **HTTPS** (Render provides this automatically)
- ✅ Enable location in browser settings
- ✅ Close browser completely and reopen after enabling

**iOS Setup:**
- Settings → Safari → Location → While Using App

**Android Setup:**
- Settings → Chrome → Permissions → Location → Allow

### 🔔 Reminder Alerts
- ✅ Allow notifications when prompted
- ✅ Keep browser tab open or in background
- ✅ Multiple alerts: notification + sound + vibration + visual popup

### 🎙️ Voice Recognition
- ✅ Use Chrome, Edge, or Safari (Firefox limited support)
- ✅ Check microphone permissions in browser
- ✅ Requires HTTPS or localhost

---

## 👨‍💻 Created By

**Mr. Avik Ghosh** • [GitHub](https://github.com/Avik-Ghosh07)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

**⭐ Star this repo if you find it helpful!**
