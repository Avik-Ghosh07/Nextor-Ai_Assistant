"""
Rate limiting utilities
"""

import datetime as dt
import logging
from typing import Dict

logger = logging.getLogger(__name__)

# In-memory rate limiting tracker
request_tracker: Dict[str, list] = {}


def check_rate_limit(client_ip: str, rate_limit: int, rate_window: int, max_ips_tracked: int) -> bool:
    """
    Simple rate limiting check. Returns True if allowed.
    
    Args:
        client_ip: Client IP address
        rate_limit: Maximum requests per window
        rate_window: Time window in seconds
        max_ips_tracked: Maximum IPs to track (prevents memory issues)
    """
    if not client_ip or client_ip == 'unknown':
        logger.warning("Rate limit check called with invalid IP")
        return True  # Allow unknown IPs but log the issue
    
    now = dt.datetime.now().timestamp()
    
    # Periodic cleanup: remove IPs with no recent activity
    if len(request_tracker) > max_ips_tracked:
        # Keep only IPs with requests in last window
        request_tracker.clear()
        logger.info(f"🧹 Cleared request_tracker (exceeded {max_ips_tracked} IPs)")
    
    if client_ip not in request_tracker:
        request_tracker[client_ip] = []
    
    # Remove old requests outside the window
    request_tracker[client_ip] = [
        req_time for req_time in request_tracker[client_ip]
        if now - req_time < rate_window
    ]
    
    # Remove IP entry if no recent requests
    if not request_tracker[client_ip]:
        del request_tracker[client_ip]
        return True
    
    # Check if limit exceeded
    if len(request_tracker[client_ip]) >= rate_limit:
        return False
    
    request_tracker[client_ip].append(now)
    return True
