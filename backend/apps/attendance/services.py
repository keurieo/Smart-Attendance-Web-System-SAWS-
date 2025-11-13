"""
Business logic services for attendance management.
"""

import jwt
import secrets
from datetime import datetime
from django.conf import settings


def generate_qr_token(session_id, expires_at):
    """
    Generate cryptographically secure JWT token for attendance session.
    
    Args:
        session_id: ID of the attendance session
        expires_at: DateTime when the token should expire
        
    Returns:
        tuple: (token_string, nonce)
    """
    nonce = secrets.token_urlsafe(16)
    
    payload = {
        'session_id': session_id,
        'nonce': nonce,
        'iat': datetime.utcnow(),
        'exp': expires_at,
        'type': 'attendance_qr'
    }
    
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token, nonce


def generate_6digit_code():
    """
    Generate random 6-digit numeric code.
    
    Returns:
        str: 6-digit code as string
    """
    return f"{secrets.randbelow(1000000):06d}"


def verify_qr_token(token):
    """
    Verify and decode JWT token.
    
    Args:
        token: JWT token string to verify
        
    Returns:
        tuple: (is_valid, payload, error_message)
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return True, payload, None
    except jwt.ExpiredSignatureError:
        return False, None, "Token expired"
    except jwt.InvalidTokenError:
        return False, None, "Invalid token"
