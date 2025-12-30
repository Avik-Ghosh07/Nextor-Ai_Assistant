
"""
Chat Controller - Chat API endpoints
"""

import logging
import datetime as dt
from flask import Blueprint, jsonify, request

from app.config.settings import Config
from app.utils.rate_limiter import check_rate_limit
from app.utils.security import clean_message, validate_message
from app.services.chat_service import generate_response

bp = Blueprint("chat", __name__)
logger = logging.getLogger(__name__)

# Assistant State Management
ASSISTANT_STATE = "IDLE"


@bp.route("/api/chat", methods=["POST"])
def chat():
    """Handle chat message and return AI response"""
    global ASSISTANT_STATE

    try:
        # 🚫 Block ONLY if assistant is sleeping
        if ASSISTANT_STATE == "SLEEP":
            logger.info(f"🚫 Request rejected - Assistant state: {ASSISTANT_STATE}")
            return jsonify({
                "error": "Assistant is sleeping",
                "state": ASSISTANT_STATE
            }), 403

        # 🔄 Auto-activate if idle
        if ASSISTANT_STATE == "IDLE":
            logger.info("🔄 Auto-activating assistant (IDLE → LISTENING)")
            ASSISTANT_STATE = "LISTENING"

        # 🔄 Move to processing
        ASSISTANT_STATE = "PROCESSING"
        logger.info("🔄 State changed: LISTENING → PROCESSING")

        # ⏱ Rate limiting
        client_ip = request.remote_addr or "unknown"
        if not check_rate_limit(
            client_ip,
            Config.RATE_LIMIT,
            Config.RATE_WINDOW,
            Config.MAX_IPS_TRACKED
        ):
            ASSISTANT_STATE = "IDLE"
            return jsonify({
                "error": "Rate limit exceeded. Please try again later."
            }), 429

        # 📥 Input validation
        data = request.get_json(silent=True)
        if not data:
            ASSISTANT_STATE = "IDLE"
            return jsonify({"error": "Invalid JSON payload"}), 400

        message = clean_message(str(data.get("message", "")))

        is_valid, error_msg = validate_message(message)
        if not is_valid:
            ASSISTANT_STATE = "IDLE"
            return jsonify({"error": error_msg}), 400

        # 🧠 Chat history
        history = data.get("history") or []
        validated_history = []

        if isinstance(history, list):
            for item in history[-10:]:
                if (
                    isinstance(item, dict)
                    and item.get("role") in ["user", "assistant"]
                    and "text" in item
                ):
                    validated_history.append({
                        "role": item["role"],
                        "text": clean_message(str(item["text"]))[:500]
                    })

        # 🤖 Generate response
        logger.info(f"💬 Processing chat: {message[:100]}...")
        reply = generate_response(message, validated_history)

        if not reply or not isinstance(reply, str):
            logger.warning("⚠️ Invalid reply from chat service")
            reply = "I'm having trouble processing that. Please try again."

        # 🔊 Speaking
        ASSISTANT_STATE = "SPEAKING"
        logger.info("🔄 State changed: PROCESSING → SPEAKING")

        response = jsonify({
            "reply": reply,
            "timestamp": dt.datetime.now().isoformat(),
            "state": ASSISTANT_STATE
        })

        # 🔄 Reset to idle after response
        ASSISTANT_STATE = "IDLE"
        logger.info("🔄 State changed: SPEAKING → IDLE")

        return response

    except Exception as e:
        logger.error("❌ Chat endpoint error", exc_info=True)
        ASSISTANT_STATE = "IDLE"
        return jsonify({"error": "Internal server error"}), 500


@bp.route("/api/assistant/state", methods=["GET"])
def get_state():
    return jsonify({
        "state": ASSISTANT_STATE,
        "timestamp": dt.datetime.now().isoformat()
    })


@bp.route("/api/assistant/state", methods=["POST"])
def set_state():
    global ASSISTANT_STATE

    try:
        data = request.get_json(silent=True)
        if not data or "state" not in data:
            return jsonify({"error": "State parameter required"}), 400

        new_state = str(data["state"]).upper()
        valid_states = ["IDLE", "LISTENING", "PROCESSING", "SPEAKING", "SLEEP"]

        if new_state not in valid_states:
            return jsonify({
                "error": f"Invalid state. Must be one of: {', '.join(valid_states)}"
            }), 400

        old_state = ASSISTANT_STATE
        ASSISTANT_STATE = new_state
        logger.info(f"🔄 State changed: {old_state} → {new_state}")

        return jsonify({
            "previous_state": old_state,
            "current_state": ASSISTANT_STATE,
            "timestamp": dt.datetime.now().isoformat()
        })

    except Exception:
        logger.error("❌ Set state error", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
