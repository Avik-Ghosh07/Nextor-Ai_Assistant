#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick start script for Nextor AI Assistant
Development server launcher
"""

if __name__ == "__main__":
    import os
    
    # Development environment settings
    os.environ['USE_WAITRESS'] = '0'  # Use Flask dev server for easier debugging
    os.environ['FLASK_ENV'] = 'development'
    
    # Import and run the MVC application
    from app import create_app
    import logging
    
    logger = logging.getLogger(__name__)
    app = create_app()
    
    port = int(os.environ.get("PORT", 5000))
    logger.info("🚀 Starting Nextor AI in DEVELOPMENT mode...")
    logger.info(f"📡 Server running on http://localhost:{port}")
    logger.info("Press Ctrl+C to stop")
    
    app.run(host="127.0.0.1", port=port, debug=True, use_reloader=False)
