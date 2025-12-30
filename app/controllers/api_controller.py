import datetime as dt
from flask import Blueprint, jsonify, send_from_directory, current_app

from llm_manager import LLMManager

bp = Blueprint("api", __name__)

llm_manager = None

def get_llm_manager():
    global llm_manager
    if llm_manager is None:
        llm_manager = LLMManager()
    return llm_manager


@bp.route("/")
def index():
    return send_from_directory(current_app.static_folder, "index.html")


@bp.route("/api/llm-status", methods=["GET"])
def llm_status():
    try:
        providers = get_llm_manager().get_available_providers()
        return jsonify({
            "available_providers": providers,
            "provider_count": len(providers),
            "has_ai": len(providers) > 0
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
    return jsonify({
        "status": "healthy",
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat()
    }), 200
