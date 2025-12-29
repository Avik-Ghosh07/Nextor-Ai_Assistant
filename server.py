"""
Nextor AI Assistant - Main Entry Point
Production-ready Flask application with MVC architecture
"""

import os
import logging
from app import create_app

logger = logging.getLogger(__name__)

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    # Get port from environment variable (for Render, Heroku, etc.) or default to 5000
    port = int(os.environ.get("PORT", 5000))
    
    # Try Waitress first, fall back to Flask dev server
    use_waitress = os.environ.get("USE_WAITRESS", "1") == "1"
    
    if use_waitress:
        try:
            from waitress import serve
            logger.info("🚀 Starting Nextor AI with Waitress server...")
            logger.info(f"📡 Server running on port {port}")
            logger.info("🌐 Also accessible at http://0.0.0.0:" + str(port))
            logger.info("Press Ctrl+C to stop the server")
            serve(app, host="0.0.0.0", port=port, threads=6)
        except ImportError:
            logger.warning("⚠️  Waitress not installed. Using Flask development server...")
            use_waitress = False
        except Exception as e:
            logger.error(f"❌ Waitress failed: {e}. Using Flask development server...")
            use_waitress = False
    
    if not use_waitress:
        logger.info("🚀 Starting Nextor AI with Flask development server...")
        logger.info(f"📡 Server running on port {port}")
        logger.info("Press Ctrl+C to stop the server")
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False, threaded=True)
