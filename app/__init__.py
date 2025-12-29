"""
Nextor AI Assistant - Flask Application Factory
"""

import logging
import sys
import os
from flask import Flask
from flask_cors import CORS

from app.config.settings import Config
from app.utils.logger import setup_logging


def create_app(config_class=Config):
    """Application factory pattern for creating Flask app"""
    
    # Setup logging first
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Create Flask app with static folder pointing to the static directory
    app = Flask(__name__, static_folder='../static', static_url_path='')
    app.config.from_object(config_class)
    
    # Initialize CORS
    CORS(app, resources={
        r"/*": {
            "origins": app.config['ALLOWED_ORIGINS'],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"],
            "max_age": 3600
        }
    })
    
    # Add security headers
    from app.utils.security import add_security_headers
    app.after_request(add_security_headers)
    
    # Register blueprints
    from app.controllers import api_controller, chat_controller, weather_controller
    
    app.register_blueprint(api_controller.bp)
    app.register_blueprint(chat_controller.bp)
    app.register_blueprint(weather_controller.bp)
    
    logger.info("🤖 Nextor AI Assistant initialized successfully")
    
    return app
