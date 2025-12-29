"""
Security utilities and middleware
"""

import re
from flask import Response


def add_security_headers(response: Response) -> Response:
    """Add security headers to all responses"""
    
    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
        "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://api.open-meteo.com https://geocoding-api.open-meteo.com; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )
    
    # Additional security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(self), microphone=(self), camera=()'
    
    return response


def clean_message(message: str) -> str:
    """Sanitize message input to prevent XSS and injection attacks."""
    # Remove any HTML tags
    message = re.sub(r'<[^>]+>', '', message)
    # Remove script tags and event handlers
    message = re.sub(r'on\w+\s*=', '', message, flags=re.IGNORECASE)
    # Remove javascript: protocol
    message = re.sub(r'javascript:', '', message, flags=re.IGNORECASE)
    # Remove data: protocol
    message = re.sub(r'data:', '', message, flags=re.IGNORECASE)
    # Limit to printable ASCII and common Unicode
    message = ''.join(char for char in message if char.isprintable() or char.isspace())
    return message.strip()


def validate_message(message: str) -> tuple[bool, str]:
    """Validate message content and return (is_valid, error_message)"""
    
    if not message:
        return False, "Message cannot be empty"
    
    if len(message) > 1000:
        return False, "Message too long (max 1000 characters)"
    
    if len(message) < 1:
        return False, "Message too short"
    
    # Validate message doesn't contain suspicious patterns
    suspicious_patterns = [r'<script', r'javascript:', r'onerror=', r'onclick=', r'eval\(']
    for pattern in suspicious_patterns:
        if re.search(pattern, message, re.IGNORECASE):
            return False, "Invalid message content"
    
    return True, ""
