"""
Application Configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""
    
    # Security configurations
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(32).hex())
    MAX_CONTENT_LENGTH = 16 * 1024  # 16KB max request size
    JSON_SORT_KEYS = False
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True  # Prevent XSS
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    
    # CORS configuration
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')
    
    # Rate limiting
    RATE_LIMIT = int(os.getenv('RATE_LIMIT', '60'))  # requests per minute
    RATE_WINDOW = 60  # seconds
    MAX_IPS_TRACKED = 1000  # Prevent memory issues
    
    # Server configuration
    PORT = int(os.environ.get("PORT", 5000))
    USE_WAITRESS = os.environ.get("USE_WAITRESS", "1") == "1"
