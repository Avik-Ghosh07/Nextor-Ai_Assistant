"""
Nextor AI Assistant - Main Entry Point
Production-ready Flask application with MVC architecture
"""

import os
import logging
from app import create_app

# Configure logging (important, otherwise logs may not show)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    # Read PORT from environment (Render/Heroku) or default to 5000
    port = int(os.environ.get("PORT", 5000))

    # Use Waitress only if explicitly enabled
    use_waitress = os.environ.get("USE_WAITRESS", "1") == "1"

    if use_waitress:
        try:
            from waitress import serve

            logger.info("🚀 Starting Nextor AI with Waitress server...")
            logger.info(f"📡 Server running on port {port}")
            logger.info(f"🌐 Open in browser: http://localhost:{port}")
            logger.info("Press Ctrl+C to stop the server")

            # IMPORTANT: use 0.0.0.0 for deployment compatibility
            serve(app, host="0.0.0.0", port=port, threads=6)

        except ImportError:
            logger.warning("⚠️ Waitress not installed. Falling back to Flask dev server.")
            use_waitress = False

        except Exception as e:
            logger.error(f"❌ Waitress failed: {e}. Falling back to Flask dev server.")
            use_waitress = False

    if not use_waitress:
        logger.info("🚀 Starting Nextor AI with Flask development server...")
        logger.info(f"📡 Server running on port {port}")
        logger.info(f"🌐 Open in browser: http://localhost:{port}")
        logger.info("Press Ctrl+C to stop the server")

        app.run(
            host="0.0.0.0",
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True
        )
