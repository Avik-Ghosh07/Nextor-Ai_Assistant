"""
Weather Controller - Weather API endpoints
"""

import logging
import requests
from flask import Blueprint, jsonify, request

from app.config.settings import Config
from app.utils.rate_limiter import check_rate_limit
from app.utils.helpers import safe_float
from app.services.weather_service import get_weather_data

bp = Blueprint('weather', __name__)
logger = logging.getLogger(__name__)


@bp.route("/api/weather", methods=["GET"])
def weather():
    """Get weather data for given coordinates"""
    try:
        # Rate limiting
        client_ip = request.remote_addr or 'unknown'
        if not check_rate_limit(
            client_ip, 
            Config.RATE_LIMIT, 
            Config.RATE_WINDOW, 
            Config.MAX_IPS_TRACKED
        ):
            return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429
        
        lat = safe_float(request.args.get("lat"))
        lon = safe_float(request.args.get("lon"))

        if lat is None or lon is None:
            return jsonify({"error": "lat and lon parameters are required"}), 400
        
        # Validate coordinates
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return jsonify({"error": "Invalid coordinates"}), 400

        weather_data = get_weather_data(lat, lon)
        return jsonify(weather_data)
        
    except (requests.RequestException, ValueError) as exc:
        return jsonify({"error": "Unable to fetch weather data", "details": str(exc)}), 502
    except Exception as e:
        logger.error(f"Weather endpoint error: {e}")
        return jsonify({"error": "Internal server error"}), 500
