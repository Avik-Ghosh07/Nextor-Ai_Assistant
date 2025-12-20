# Nextor — AI Voice Assistant 🎙️

> **Your intelligent voice companion with enterprise-grade code quality**

A production-ready AI assistant combining voice recognition, natural language processing, and real-time web services. Built with **FAANG-level engineering standards** featuring comprehensive logging, type safety, and security hardening.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code Quality](https://img.shields.io/badge/Code%20Quality-FAANG%20Level-brightgreen.svg)]()

**⚡ Tech Stack:** Python Flask · Google Gemini AI · Web Speech API · Tailwind CSS

---

## ✨ What Makes This Special

🛡️ **Production Ready** - Enterprise logging, type hints, comprehensive error handling  
🔒 **Security First** - Input validation, XSS prevention, CORS, rate limiting  
📱 **Mobile Optimized** - Works flawlessly on phones with haptic feedback  
🧠 **Smart Fallbacks** - Works without API keys using web search + built-in knowledge  
🎨 **Modern UI** - Glass morphism design with smooth animations  
⚡ **Zero Setup** - Deploy in 2 minutes or run locally instantly

---

## 🚀 Quick Start

<details>
<summary><b>🌐 Deploy to Render (Recommended - Free)</b></summary>

1. **Fork this repo** → [render.com](https://render.com) → Create Web Service
2. **Connect GitHub** → Auto-detects `render.yaml`
3. **Add API Key** (Optional): `GEMINI_API_KEY` from [Google AI Studio](https://makersuite.google.com/app/apikey)
4. **Deploy!** → Live in ~2 minutes

</details>

<details>
<summary><b>💻 Run Locally</b></summary>

```bash
# Clone and setup
git clone https://github.com/Avik-Ghosh07/Nextor-Ai_Assistant.git
cd Nextor-Ai_Assistant

# Install dependencies
pip install -r requirements.txt

# Run server (with Waitress WSGI)
python server.py
```

Open **http://127.0.0.1:5000** → Allow permissions → Start talking!

**Environment Variables** (Optional):
```bash
GEMINI_API_KEY=your_key    # For AI features (works without it)
ALLOWED_ORIGINS=*          # CORS configuration
RATE_LIMIT=60              # Requests per minute
```

</details>

---

## 🎯 Core Features

| Feature | Description |
|---------|-------------|
| 🎙️ **Voice Control** | Natural speech recognition with text-to-speech responses |
| 🤖 **AI Chat** | Google Gemini 2.0 Flash with smart web search fallback |
| ⏰ **Smart Reminders** | Natural language parsing ("in 10 minutes", "at 6 PM") |
| 🌤️ **Live Weather** | Auto-location with real-time updates and advice |
| 🎵 **Music Player** | YouTube integration for Hindi, English, Bengali songs |
| 🧮 **Calculator** | Voice-activated math ("what is 25 times 4") |
| 🔍 **Web Search** | Integrated Wikipedia, DuckDuckGo, Google search |
| 💡 **Productivity** | Tips, motivational quotes, work-life balance advice |
| 📱 **Responsive** | Optimized for mobile, tablet, desktop (iOS 12+, Android 5+) |

---

## 🏗️ Engineering Excellence

<details>
<summary><b>🐍 Backend Architecture (Python/Flask)</b></summary>

- ✅ **Type Safety**: Full type hints (Python 3.8+ compatible with `Optional`, `Union`)
- ✅ **Logging**: Professional logging system (`logs/nextor.log`) with rotation
- ✅ **Error Handling**: Try-catch blocks with graceful degradation
- ✅ **Security**: Input sanitization, XSS prevention, CORS, rate limiting
- ✅ **Production Server**: Waitress WSGI for scalability
- ✅ **API Design**: RESTful endpoints with proper HTTP status codes
- ✅ **Clean Code**: PEP 8 compliant, comprehensive docstrings

</details>

<details>
<summary><b>💻 Frontend Architecture (JavaScript)</b></summary>

- ✅ **Modern ES6+**: Async/await, arrow functions, template literals
- ✅ **Security**: HTML escaping, CSP headers, input validation
- ✅ **UX**: Loading states, error feedback, haptic vibrations
- ✅ **Storage**: LocalStorage with quota management and error handling
- ✅ **Responsive**: Mobile-first with Tailwind CSS
- ✅ **Accessibility**: Semantic HTML, ARIA labels, keyboard navigation

</details>

<details>
<summary><b>🔒 Security Features</b></summary>

- Input validation and sanitization on both client and server
- XSS prevention with HTML escaping and CSP headers
- CORS protection with configurable origins
- Rate limiting (60 req/min per IP, configurable)
- Security headers: HSTS, X-Frame-Options, X-Content-Type-Options
- No data collection - all data stored locally in browser

</details>

---

## 🎤 Voice Commands Examples

```bash
# Music & Entertainment
"play a hindi song" | "play Shape of You" | "tell me a joke"

# Information
"what's the weather" | "what time is it" | "who is Jensen Huang"

# Reminders
"remind me to call mom in 10 minutes" | "remind me at 6:30 PM"

# Productivity
"motivate me" | "give me productivity tips" | "career advice"

# Navigation
"open youtube" | "search for climate change" | "calculate 25 times 4"
```

<details>
<summary><b>📋 Full Command List</b></summary>

**Time & Date**: time, date, day  
**Weather**: weather, temperature  
**Music**: play [song/language], stop music  
**Reminders**: remind me, set reminder  
**Search**: search for, google, find  
**Apps**: open [youtube/gmail/whatsapp/etc]  
**Math**: calculate, what is [math expression]  
**Fun**: joke, fun fact, flip a coin, roll dice  
**Productivity**: productivity tips, motivation, study tips, career advice  
**Teach**: Custom responses via UI

</details>

---

## 🔧 Troubleshooting

<details>
<summary><b>📱 Mobile Issues</b></summary>

**Location not working?**
- Must use HTTPS (Render provides automatically)
- iOS: Settings → Safari → Location → While Using App
- Android: Settings → Chrome → Permissions → Location → Allow

**Notifications not showing?**
- Allow notifications when prompted
- Check browser settings
- Keep tab active or in background

</details>

<details>
<summary><b>🐛 Technical Issues</b></summary>

**Voice recognition not working?**
- Use Chrome, Edge, or Safari (best support)
- Check microphone permissions
- Requires HTTPS or localhost

**Debugging:**
- Browser console: Press F12
- Server logs: `logs/nextor.log`
- Test endpoint: `http://localhost:5000/api/health`

</details>

---

## 📊 Project Stats

| Metric | Value |
|--------|-------|
| **Total Lines** | ~4,000+ |
| **Languages** | Python, JavaScript, HTML, CSS |
| **API Endpoints** | 3 RESTful endpoints |
| **Security Features** | 8+ implemented |
| **Browser Support** | 95%+ modern browsers |
| **Mobile Support** | iOS 12+, Android 5+ |

---

## 🤝 Contributing

Contributions welcome! Please see our guidelines:

1. Fork → Create branch (`feature/AmazingFeature`)
2. Commit (`git commit -m 'feat: Add feature'`)
3. Push → Open Pull Request

**Standards**: PEP 8, type hints, docstrings, test on multiple browsers

---

## 📈 Roadmap

**Coming Soon:**
- [ ] 🌍 Multi-language support (Hindi,Bengali, Spanish, French)
- [ ] 🎚️ Voice customization (speed, pitch, accent)
- [ ] 📴 Offline mode with service workers
- [ ] 🧩 Browser extension for quick access
- [ ] 📱 Native mobile app (React Native)

**Future Plans:**
- [ ] 📅 Calendar integration (Google, Outlook)
- [ ] 📧 Email notifications for reminders
- [ ] 📊 Analytics dashboard
- [ ] 🔌 Plugin system for custom commands

---

## 👨‍💻 Author

**Avik Ghosh** · [GitHub](https://github.com/Avik-Ghosh07)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

<div align="center">

**⭐ Star this repo if you find it helpful!**

Made with ❤️ and enterprise-level engineering practices

</div>
