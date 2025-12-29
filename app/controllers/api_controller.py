"""
API Controller - General API endpoints
"""

import datetime as dt
from flask import Blueprint, jsonify, send_from_directory

from llm_manager import LLMManager

bp = Blueprint('api', __name__)

# Initialize LLM Manager
llm_manager = LLMManager()


@bp.route("/")
def index():
    """Serve the main HTML file"""
    return send_from_directory('../static', "index.html")


@bp.route("/api/llm-status", methods=["GET"])
def llm_status():
    """Get status of available LLM providers"""
    try:
        available_providers = llm_manager.get_available_providers()
        return jsonify({
            "available_providers": available_providers,
            "provider_count": len(available_providers),
            "has_ai": len(available_providers) > 0
        })
    except Exception as e:
        return jsonify({
            "available_providers": [],
            "provider_count": 0,
            "has_ai": False,
            "error": str(e)
        }), 500


@bp.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint with minimal information disclosure."""
    return jsonify({
        "status": "healthy",
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat()
    }), 200
