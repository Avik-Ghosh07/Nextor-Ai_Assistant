# Nextor AI Assistant

**Created by Avik Ghosh**

A powerful multi-LLM AI assistant with web search and weather capabilities. Supports multiple AI providers including OpenAI GPT-4, Anthropic Claude, Groq, Google Gemini, and local Ollama models. Built with clean MVC architecture for maintainability and scalability.

## ✨ Features

### Multi-LLM Support
- **OpenAI GPT-4** - Industry-leading AI with superior reasoning
- **Anthropic Claude 3.5** - Excellent for coding and analysis
- **Groq Llama 3.1** - Ultra-fast inference with free tier
- **Google Gemini Pro** - Google's latest AI with generous free quota
- **Ollama** - Run models locally for complete privacy
- **Automatic Fallback** - Seamlessly switches providers if one fails

### Intelligent Search & Data
- **Web Search** - Integrated Wikipedia, DuckDuckGo, and Google Custom Search
- **Real-time Weather** - Current conditions and forecasts via OpenWeatherMap API
- **Built-in Knowledge** - Handles math, programming questions, and general knowledge offline

### Production-Ready Architecture
- **MVC Pattern** - Clean separation of concerns across 20+ well-organized files
- **Security** - XSS prevention, CORS protection, rate limiting, input sanitization
- **Logging** - Comprehensive logging system for debugging and monitoring
- **Error Handling** - Graceful degradation and detailed error messages

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- API key for at least one LLM provider (see [Getting API Keys](#getting-api-keys))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Nextor-Ai-Assistant
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Mac/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys (see below)
   ```

5. **Run the application**
   ```bash
   # Development mode (with auto-reload)
   python start_server.py
   
   # Production mode (optimized with Waitress)
   python server.py
   ```

6. **Open in browser**
   ```
   http://localhost:5000
   ```

## ⚙️ Configuration

Create a `.env` file in the project root with your API keys. You need **at least one LLM provider** to be configured:

```env
# LLM Providers (configure at least one)
OPENAI_API_KEY=sk-proj-...              # OpenAI GPT-4
ANTHROPIC_API_KEY=sk-ant-api-...        # Anthropic Claude
GROQ_API_KEY=gsk_...                    # Groq (FREE)
GEMINI_API_KEY=AIza...                  # Google Gemini (FREE)

# Optional Services
WEATHER_API_KEY=...                      # OpenWeatherMap (optional)
GOOGLE_CSE_ID=...                        # Google Custom Search (optional)
GOOGLE_API_KEY=...                       # Google API (optional)
```

### Getting API Keys

| Provider | URL | Cost | Notes |
|----------|-----|------|-------|
| **OpenAI** | [platform.openai.com](https://platform.openai.com/api-keys) | Pay-per-use | Best quality, trial credits available |
| **Anthropic** | [console.anthropic.com](https://console.anthropic.com) | Pay-per-use | Excellent for code, trial credits |
| **Groq** | [console.groq.com](https://console.groq.com) | **FREE** | Ultra-fast, generous free tier |
| **Gemini** | [makersuite.google.com](https://makersuite.google.com/app/apikey) | **FREE** | Good quality, 60 req/min free |
| **Ollama** | [ollama.ai](https://ollama.ai) | **FREE** | Runs locally, complete privacy |
| **Weather** | [openweathermap.org](https://openweathermap.org/api) | FREE tier | Optional for weather features |

### Ollama Setup (Optional - Local Models)

For completely free and private AI:

```bash
# 1. Install Ollama from ollama.ai
# 2. Pull models
ollama pull llama2      # General purpose
ollama pull mistral     # Fast and capable
ollama pull codellama   # Optimized for code

# 3. Start Ollama server
ollama serve
```

No API key needed - runs 100% locally!

## 📁 Project Structure

The project follows clean MVC (Model-View-Controller) architecture:

```
Nextor-Ai-Assistant/
├── app/                          # Main application package
│   ├── __init__.py              # Flask app factory
│   ├── __version__.py           # Version info
│   │
│   ├── config/                  # Configuration
│   │   └── settings.py          # App settings and constants
│   │
│   ├── controllers/             # HTTP request handlers
│   │   ├── api_controller.py    # General API endpoints
│   │   ├── chat_controller.py   # Chat/AI endpoints
│   │   └── weather_controller.py # Weather endpoints
│   │
│   ├── services/                # Business logic layer
│   │   ├── chat_service.py      # AI chat integration
│   │   ├── weather_service.py   # Weather data processing
│   │   └── web_search_service.py # Web search functionality
│   │
│   ├── models/                  # Data models and constants
│   │   ├── knowledge_base.py    # Built-in knowledge
│   │   └── weather_codes.py     # Weather condition mappings
│   │
│   └── utils/                   # Utility functions
│       ├── helpers.py           # Helper functions
│       ├── logger.py            # Logging configuration
│       ├── rate_limiter.py      # Rate limiting
│       └── security.py          # Security utilities
│
├── static/                      # Frontend files
│   ├── index.html              # Main UI
│   ├── script.js               # Client-side JavaScript
│   └── style.css               # Styling
│
├── backup/                      # Archived old files
├── logs/                        # Application logs
│   └── nextor.log
│
├── llm_manager.py              # LLM provider integration
├── server.py                   # Production entry point
├── start_server.py             # Development server
├── requirements.txt            # Python dependencies
└── .env                        # Environment variables (create from .env.example)
```

## 🎯 Usage

1. **Select AI Provider** - Choose from dropdown or let system auto-select
2. **Ask Questions** - Type or speak your question
3. **Get Responses** - AI responds with web search and weather integration

### Example Queries

```
"What's the weather in London?"
"Explain quantum computing"
"Write a Python function to sort a list"
"Search for latest AI news"
"Calculate 15% of 250"
```

## 🔌 API Endpoints

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/` | GET | Main UI | - |
| `/api/health` | GET | Health check | - |
| `/api/chat` | POST | Chat with AI | `message`, `provider` (optional) |
| `/api/weather` | GET | Get weather | `location` |

### Example API Call

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "provider": "groq"}'
```

## 🛠️ Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Structure
- **Controllers** - Handle HTTP requests/responses only
- **Services** - Contain all business logic
- **Models** - Define data structures
- **Utils** - Reusable helper functions

### Adding New Features
1. Create service in `app/services/`
2. Add controller in `app/controllers/`
3. Register blueprint in `app/__init__.py`
4. Update frontend in `static/`

## 🚢 Deployment

### Render.com (Recommended)
1. Push code to GitHub
2. Connect repository to Render
3. Add environment variables
4. Deploy - `render.yaml` is pre-configured

### Manual Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=your_key

# Run production server
python server.py
```

Server runs on port 5000 with Waitress WSGI for production stability.

## 🐛 Troubleshooting

### Common Issues

**"No LLM provider configured"**
- Add at least one API key to `.env` file
- Restart the server after editing `.env`

**"API key invalid"**
- Verify key is correct (no extra spaces)
- Check key hasn't expired
- Regenerate key if needed

**"Port 5000 already in use"**
- Change port in `server.py`: `serve(app, port=8000)`
- Or kill process: `lsof -ti:5000 | xargs kill -9` (Mac/Linux)

**"Module not found" errors**
- Activate virtual environment: `.venv\Scripts\activate`
- Reinstall: `pip install -r requirements.txt`

**"No response from AI"**
- Check logs: `tail -f logs/nextor.log`
- Verify API key is valid
- Try different provider
- Check internet connection

**Ollama not working**
- Start Ollama: `ollama serve`
- Pull a model: `ollama pull llama2`
- Verify port 11434 is open

### Debug Mode

Enable detailed logging in `.env`:
```env
FLASK_DEBUG=True
LOG_LEVEL=DEBUG
```

## 📊 Dependencies

- **Flask 2.3+** - Web framework
- **Flask-CORS** - Cross-origin resource sharing
- **Waitress** - Production WSGI server
- **OpenAI** - GPT-4 API client
- **Anthropic** - Claude API client
- **Groq** - Groq API client
- **google-generativeai** - Gemini API client
- **ollama** - Local model support
- **requests** - HTTP client
- **beautifulsoup4** - Web scraping (optional)
- **python-dotenv** - Environment management

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test
4. Commit: `git commit -am 'Add feature'`
5. Push: `git push origin feature-name`
6. Submit pull request

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Check `logs/nextor.log` for errors
- **Documentation**: See code comments and docstrings
- **Updates**: Pull latest changes regularly

---

**Version**: 2.0.0  
**Architecture**: Clean MVC Pattern  
**Status**: Production Ready ✅
