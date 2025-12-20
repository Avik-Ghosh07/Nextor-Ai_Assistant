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
🛡️ **Production Ready** - FAANG-level code quality with comprehensive error handling  
📊 **Enterprise Logging** - Professional logging system for debugging and monitoring

---

## ✨ Features

- 🎙️ **Voice Recognition & AI Chat** - Powered by Google Gemini 2.0 Flash (optional)
- 📋 **Smart Reminders** - Natural language parsing with multi-modal alerts (sound + vibration + notifications)
- 🌤️ **Live Weather** - Auto-location detection with real-time updates
- 🎵 **Music & Entertainment** - YouTube playback, math calculator, quick commands
- 📱 **Fully Responsive** - Optimized for all devices from mobile to 4K
- 💾 **Local Persistence** - Reminders and chat history survive page refreshes
- 🔒 **Security Hardened** - Input validation, XSS prevention, CORS protection, rate limiting
- 📝 **Enterprise Logging** - Comprehensive logging with file and console output
- ⚡ **Type Safe** - Full Python type hints for maintainability
- 🛡️ **Error Resilient** - Graceful degradation and comprehensive error handling

---

## 🏗️ Architecture & Code Quality

### Backend (Python/Flask)
- ✅ **Type Safety**: Complete type hints (Python 3.8+ compatible)
- ✅ **Professional Logging**: Structured logging with rotation support
- ✅ **Error Handling**: Try-catch blocks with graceful fallbacks
- ✅ **Security**: Input sanitization, rate limiting, CORS policies
- ✅ **Production Server**: Waitress WSGI server for deployment
- ✅ **API Design**: RESTful endpoints with proper status codes

### Frontend (JavaScript)
- ✅ **Modern ES6+**: Async/await, arrow functions, modules
- ✅ **Security**: XSS prevention, input sanitization, CSP headers
- ✅ **Responsive**: Mobile-first design with Tailwind CSS
- ✅ **User Experience**: Loading states, error feedback, haptic feedback
- ✅ **Local Storage**: Persistent data with quota management
- ✅ **Accessibility**: Semantic HTML, ARIA labels, keyboard navigation

### Code Standards
- 📋 **PEP 8 Compliant**: Python code follows official style guide
- 📋 **Documented**: Comprehensive docstrings and comments
- 📋 **Maintainable**: Single responsibility, DRY principles
- 📋 **Testable**: Modular design with clear interfaces
- 📋 **Version Controlled**: Semantic versioning, clear commit messages

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

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: Set up environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY (optional)

# Run the server
python server.py
```
Open http://127.0.0.1:5000 → Allow microphone/notifications/location → Click "Activate Nextor"

**Note:** Works without Gemini API using pattern-based fallback responses.

### Environment Variables
```bash
# .env file (optional)
GEMINI_API_KEY=your_api_key_here  # Optional: For AI features
ALLOWED_ORIGINS=*                  # CORS: * for dev, specify domains for production
RATE_LIMIT=60                      # Requests per minute per IP
```

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

### 🐛 Debugging
- ✅ Check browser console for errors (F12)
- ✅ Server logs available in `logs/nextor.log`
- ✅ Enable debug mode by checking terminal output
- ✅ Test API endpoints: `http://localhost:5000/api/health`

---

## 📊 Project Statistics

- **Lines of Code**: ~4,000+ (Python + JavaScript)
- **API Endpoints**: 3 RESTful endpoints
- **Security Features**: 8+ (CORS, CSP, XSS prevention, rate limiting, etc.)
- **Dependencies**: 8 Python packages (all production-ready)
- **Browser Support**: Chrome, Edge, Safari, Firefox (95%+ modern browsers)
- **Mobile Support**: iOS 12+, Android 5+

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

**Code Standards:**
- Follow PEP 8 for Python
- Use type hints for all functions
- Add docstrings and comments
- Test on multiple browsers
- Ensure mobile responsiveness

---

## 🔒 Security

- **Input Validation**: All user inputs sanitized
- **XSS Prevention**: HTML escaping and CSP headers
- **CORS Protection**: Configurable allowed origins
- **Rate Limiting**: 60 requests/minute per IP (configurable)
- **Secure Headers**: HSTS, X-Frame-Options, CSP, etc.
- **No Data Collection**: All data stored locally in browser

**Found a security issue?** Please email or create a private security advisory.

---

## 📈 Roadmap

- [ ] Multi-language support (Hindi, Spanish, French)
- [ ] Voice customization (speed, pitch, accent)
- [ ] Offline mode with service workers
- [ ] Browser extension for quick access
- [ ] Mobile app (React Native)
- [ ] Calendar integration (Google Calendar, Outlook)
- [ ] Email notifications for reminders
- [ ] Advanced analytics dashboard
- [ ] Plugin system for custom commands
- [ ] Team collaboration features

---

## 👨‍💻 Created By

**Mr. Avik Ghosh** • [GitHub](https://github.com/Avik-Ghosh07)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

**⭐ Star this repo if you find it helpful!**
